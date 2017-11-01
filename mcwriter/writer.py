"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
import datetime
import json
import csv
import time
import traceback
import os
from keboola import docker
from requests import HTTPError
from .exceptions import UserError, ConfigError
from .utils import (serialize_lists_input,
                    serialize_members_input,
                    serialize_tags_input,
                    prepare_batch_data_add_members,
                    prepare_batch_data_delete_members,
                    write_batches_to_csv,
                    prepare_batch_data_update_members,
                    _setup_client,
                    wait_for_batch_to_finish)

# valid fields for creating mailing list according to
# https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists
FILE_NEW_LISTS = 'new_lists.csv'
FILE_UPDATE_LISTS = 'update_lists.csv'
FILE_ADD_MEMBERS = 'add_members.csv'
FILE_ADD_TAGS = 'add_tags.csv'
FILE_DELETE_MEMBERS = 'delete_members.csv'
FILE_UPDATE_MEMBERS = 'update_members.csv'
PATH_OUT_BATCHES_DELETE = '/data/out/tables/delete_members_batches.csv'
PATH_OUT_BATCHES_UPDATE = '/data/out/tables/update_members_batches.csv'
PATH_OUT_BATCHES_ADD = '/data/out/tables/add_members_batches.csv'
BATCH_THRESHOLD = 5 # When to switch from serial jobs to batch jobs
BATCH_DELAY = 0.5 #seconds between submitting batches
SEQUENTIAL_REQUEST_DELAY = 0.8 #seconds between sequential requests
BATCH_WAIT_DELAY = 5 #seconds, there is linear growth polling implemented

LISTS_VALID_FIELDS = ["name",
                      "contact.company", "contact.address1", "contact.address2",
                      "contact.city", "contact.state", "contact.zip", "contact.country",
                      "contact.phone",
                      "permission_reminder", "use_archive_bar",
                      "campaign_defaults.from_name", "campaign_defaults.from_email",
                      "campaign_defaults.subject", "campaign_defaults.language",
                      "notify_on_subscribe",
                      "notify_on_unsubscribe",
                      "email_type_option",
                      "visibility"]

def set_up(path_config='/data/'):
    '''Initial setup, config parsing etc.
    '''
    cfg = docker.Config(path_config)
    params = cfg.get_parameters()
    tables = cfg.get_input_tables()
    if params.get('debug'):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    client = _setup_client(params)
    return client, params, tables


def show_lists():
    """Show existing mailing lists"""
    pass


def _create_lists_serial(client, serialized_data):
    """Create lists. Optionally, return the mapping to real ids

    Returns:
        a mapping of {custom_list_id: real_list_id} for every created list
    """
    logging.debug('Creating lists in serial.')
    created_lists = {}
    for data in serialized_data:
        try:
            resp = client.lists.create(data=data)
            custom_id = data.get('custom_id')
            if custom_id:
                created_lists[custom_id] = resp['id']
            time.sleep(SEQUENTIAL_REQUEST_DELAY)
        except HTTPError as exc:
            err_resp = json.loads(exc.response.text)
            logging.error("Error while creating request:\n"
                          "POST data:\n%s"
                          "Error message\n%s", data, err_resp)
            raise

    return created_lists

def create_lists(client, csv_lists):
    """Create new mailing list

    The reason for this wrapper function is that it is possible to create lists
    in batch. A function once present, but removed because it is PITA to
    retrieve the results created by the batch job and probably not worth the
    hassle, since one is not expected to create hundreds of lists.

    """
    serialized_data = serialize_lists_input(csv_lists)
    logging.debug("Creating %d new lists defined in %s", len(serialized_data), csv_lists)
    created_lists = _create_lists_serial(client=client, serialized_data=serialized_data)
    logging.info("New lists created.")
    return created_lists


def update_lists(client, csv_lists):
    """Update existing mailing lists

    the input csv file should have the same structure as for lists creation
    with an additional column `list_id` used to reference existing lists.
    """
    serialized_data = serialize_lists_input(csv_lists)
    logging.debug("Updating %d new lists defined in %s", len(serialized_data), csv_lists)
    _update_lists_serial(client=client, serialized_data=serialized_data)
    logging.info("Lists updated.")


def _update_lists_serial(client, serialized_data):
    for data in serialized_data:
        list_id = data.pop('list_id')
        try:
            client.lists.update(list_id=list_id, data=data)
        except HTTPError as exc:
            err_resp = json.loads(exc.response.text)
            logging.error("Error while creating request:\n"
                          "POST data:\n%s"
                          "Error message\n%s", data, err_resp)
            raise
        time.sleep(0.2)

    logging.info("")


def _update_members_serial(client, serialized_data):
    """Add members to list"""
    logging.debug('Updating members serially')
    for data in serialized_data:
        try:
            client.lists.members.update(data=data,
                                        list_id=data.pop('list_id'),
                                        subscriber_hash=data.pop('subscriber_hash'))
        except HTTPError as exc:
            err_resp = json.loads(exc.response.text)
            logging.error("Error while creating request:\n"
                          "POST data:\n%s\n"
                          "Error message\n%s", data, err_resp)
            raise


def _update_members_in_batch(client, serialized_data):
    operation_id = 'update_members_{:%Y%m%d:%H-%M-%S}'.format(
        datetime.datetime.now())
    logging.debug('updating members in batch mode: operation_id %s', operation_id)

    operations = prepare_batch_data_update_members(serialized_data)
    try:
        batch_response = client.batches.create(data=operations)
        logging.debug("Got batch response: %s", batch_response)
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating batch request:\n%s\nAborting.", err_resp)
        raise
    else:
        return batch_response  # should contain operation_id if we later need this

def _delete_members_in_batch(client, serialized_data):
    operation_id = 'delete_members_{:%Y%m%d:%H-%M-%S}'.format(
        datetime.datetime.now())
    logging.debug('deleting members in batch mode: operation_id %s', operation_id)

    operations = prepare_batch_data_delete_members(serialized_data)
    try:
        batch_response = client.batches.create(data=operations)
        logging.debug("Got batch response: %s", batch_response)
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating batch request:\n%s\nAborting.", err_resp)
        raise
    else:
        return batch_response  # should contain operation_id if we later need this

def _add_members_serial(client, serialized_data):
    """Add members to list"""
    logging.debug('Adding members to lists in serial.')
    for data in serialized_data:
        try:
            client.lists.members.create_or_update(data=data,
                                                  list_id=data.pop('list_id'),
                                                  subscriber_hash=data.pop('subscriber_hash'))
        except HTTPError as exc:
            err_resp = json.loads(exc.response.text)
            logging.error("Error while creating request:\n"
                          "POST data:\n%s\n"
                          "Error message\n%s", data, err_resp)
            raise


def _add_members_in_batch(client, serialized_data):
    operation_id = 'add_members_{:%Y%m%d:%H-%M-%S}'.format(
        datetime.datetime.now())
    logging.debug('Adding members in batch mode: operation_id %s', operation_id)

    operations = prepare_batch_data_add_members(serialized_data)
    try:
        batch_response = client.batches.create(data=operations)
        logging.debug("Got batch response: %s", batch_response)
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating batch request:\n%s\nAborting.", err_resp)
        raise
    else:
        return batch_response  # should contain operation_id if we later need this


def delete_members(client, csv_members):
    """
    Delete members of given lists. Always in batch

    parse data from csv (csv_members arugment)
    """

    logging.info("Deleting members to list as described in %s", csv_members)
    batches = _do_members_action_and_wait_for_batch(client,
                                          csv_members,
                                          action='delete',
                                          batch_action=_delete_members_in_batch,
                                          batch=True)
    return batches

def update_members(client, csv_members, batch=None):
    """
    Update members of given lists.

    parse data from csv (csv_members arugment)
    """
    logging.info("Updating members to list as described in %s", csv_members)
    batches = _do_members_action_and_wait_for_batch(client,
                                          csv_members,
                                          action='update',
                                          batch_action=_update_members_in_batch,
                                          serial_action=_update_members_serial)

    return batches

def _do_members_action_and_wait_for_batch(client,
                                          csv_members,
                                          action,
                                          batch_action,
                                          serial_action=None,
                                          batch=None,
                                          created_lists=None):
    running_batches = []
    completed_batches = []
    processed = 0
    for serialized_data in serialize_members_input(csv_members,
                                                   action=action,
                                                   created_lists=created_lists):
        no_members = len(serialized_data)
        processed += no_members
        logging.info("So far processed %s rows", processed)

        if no_members <= BATCH_THRESHOLD and (batch is None or batch is False) and callable(serial_action):
            serial_action(client, serialized_data)
        else:
            logging.info("Batch job request sent")
            if len(running_batches) >= 480:
                # mailchimp limit is 500 running batches
                # It's not the most effective in the world, but I dont fell like
                # messing around with threads and stuff
                # so we just wait for one particular job to finish
                # while others might finish as well
                logging.info("There are %s running batch jobs. We need to wait"
                             "for some of them to finish before submitting new one",
                             len(running_batches))
                wait_for_this_batch = running_batches.pop(0)
                batch_status = wait_for_batch_to_finish(
                    client,
                    batch_id=wait_for_this_batch['id'],
                    api_delay=BATCH_WAIT_DELAY)
                completed_batches.append(batch_status)
            batch_response = batch_action(client, serialized_data)
            running_batches.append(batch_response)
            time.sleep(BATCH_DELAY)

    # processed_batches = []
    logging.info("Waiting for batches to finish.")
    while running_batches:
        batch_response = running_batches.pop()
        # batch_response in running_batches:
        # Wait untill all batches are finished
        batch_status = wait_for_batch_to_finish(client, batch_id=batch_response['id'],
                                                api_delay=SEQUENTIAL_REQUEST_DELAY)
        completed_batches.append(batch_status)
    return completed_batches

def add_members_to_lists(client, csv_members, batch=None, created_lists=None):
    """Add members to list. Update if they are already there.

    Parse data from csv (default /data/in/tables/add_members.csv)
    """
    logging.info("Adding members to list as described in %s", csv_members)
    batches = _do_members_action_and_wait_for_batch(client,
                                                    csv_members,
                                                    action='add_or_update',
                                                    created_lists=created_lists,
                                                    serial_action=_add_members_serial,
                                                    batch_action=_add_members_in_batch)
    return batches


def create_tags(client, csv_tags, created_lists=None):
    serialized_tags = serialize_tags_input(csv_tags, created_lists=created_lists)
    logging.info("Adding %s tags to lists", len(serialized_tags))
    for tag in serialized_tags:
        # at this point we need th real list id
        list_id = tag.pop('list_id')
        client.lists.merge_fields.create(list_id, tag)
    logging.info("Tags created.")


def run_update_lists(client, csv_lists):
    """Run the writer only updating tables

    The reason for the wrapper function is that sometimes in the future we
    might want to implement batch updating of lists
    Args:
        client: a mailchimp3.MailChimp instance
        csv_lists: path/to/update_lists.csv
    """
    update_lists(client, csv_lists=csv_lists)


def run():
    try:
        datadir = os.getenv("KBC_DATADIR")
        client, params, tables = set_up(path_config=datadir)
        run_writer(client, params, tables, datadir=datadir)
    except (UserError, HTTPError) as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(err, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)


def run_writer(client, params, tables, datadir):
    """Analyze which tables are defined and act accordingly

    Four combinations of input files are possible:

    #. If only table `new_lists.csv` exists, the writer creates lists in the
    table. If only table `update_lists.csv` exists, the writer updates lists in
    mailchimp based on values defined in the input table.

    #. If only table `add_members.csv` exists, the writer adds defined members
    to existing lists. The `add_members.csv` file must contain column `list_id`
    containing valid list id from the mailchimp website

    #. if table `update_lists.csv` exists, the writer updates the defined lists
      and exits. No adding of members occurs, do that in a new writer.

    #. If you supply both tables `new_lists.csv` and `add_members.csv`; first,
      the lists defined in `new_lists.csv` are created. Next, emails defined in
      `add_members.csv` are added to the newly created lists based on the
      `custom_id` column is used as a foreign key to the column
      `custom_list_id` in `add_members.csv` table (make sure to supply both!)

    """

    logging.debug("Running writer")
    tablenames = [t['full_path'] for t in tables]

    logging.debug("Got tablenames %s", tablenames)
    path_update_lists = os.path.join(datadir, 'in/tables', FILE_UPDATE_LISTS)
    path_new_lists = os.path.join(datadir, 'in/tables', FILE_NEW_LISTS)
    path_add_members = os.path.join(datadir, 'in/tables', FILE_ADD_MEMBERS)
    path_update_members = os.path.join(datadir, 'in/tables', FILE_UPDATE_MEMBERS)
    path_add_tags = os.path.join(datadir, 'in/tables', FILE_ADD_TAGS)
    path_delete_members = os.path.join(datadir, 'in/tables', FILE_DELETE_MEMBERS)

    outbucket = params.get('results_bucket', 'in.c-mailchimp-writer')

    created_lists = {}
    #1. update_lists.csv
    #2. new_lists.csv
    #3. add_tags.csv
    #4. add_members.csv

    if len(tablenames) == 0:
        raise ConfigError("No input tables specified!")

    if path_update_lists in tablenames:
        update_lists(client, csv_lists=path_update_lists)
    if path_new_lists in tablenames:
        created_lists = create_lists(client, csv_lists=path_new_lists)
    if path_add_tags in tablenames:
        create_tags(client, csv_tags=path_add_tags, created_lists=created_lists)
    if path_add_members in tablenames:
        batches = add_members_to_lists(client=client, csv_members=path_add_members,
                             created_lists=created_lists)
        if batches:
            write_batches_to_csv(batches, PATH_OUT_BATCHES_ADD, bucketname=outbucket)
    if path_update_members in tablenames:
        batches = update_members(client, csv_members=path_update_members)
        if batches:
            write_batches_to_csv(batches, PATH_OUT_BATCHES_UPDATE, bucketname=outbucket)

    if path_delete_members in tablenames:
        batches = delete_members(client, csv_members=path_delete_members)
        if batches:
            write_batches_to_csv(batches, PATH_OUT_BATCHES_DELETE, bucketname=outbucket)
    logging.info("Writer finished")

