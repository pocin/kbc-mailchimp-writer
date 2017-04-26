"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
import datetime
import json
import time
import traceback
from keboola import docker
from requests import HTTPError
from .utils import (serialize_lists_input,
                    serialize_members_input,
                    prepare_batch_data_add_members,
                    _setup_client)

# valid fields for creating mailing list according to
# https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists
PATH_NEW_LISTS = '/data/in/tables/new_lists.csv'
PATH_UPDATE_LISTS = '/data/in/tables/update_lists.csv'
PATH_ADD_MEMBERS = '/data/in/tables/add_members.csv'
BATCH_THRESHOLD = 3 # When to switch from serial jobs to batch jobs
SEQUENTIAL_REQUEST_DELAY = 0.3 #seconds between sequential requests

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

    client = _setup_client(params)
    return client, params, tables


def show_lists():
    """Show existing mailing lists"""
    pass


def _create_lists_serial(client, serialized_data):
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

def create_lists(client, csv_lists=PATH_NEW_LISTS):
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


def update_lists(client, csv_lists=PATH_UPDATE_LISTS):
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
            sys.exit(1)
        time.sleep(0.2)

    logging.info("")


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
                          "POST data:\n%s"
                          "Error message\n%s", data, err_resp)
            sys.exit(1)


def _add_members_in_batch(client, serialized_data):
    operation_id = 'add_members_{:%Y%m%d:%H-%M-%S}'.format(
        datetime.datetime.now())
    logging.debug('Creating lists in batch mode: operation_id %s', operation_id)

    operations = prepare_batch_data_add_members(serialized_data)
    try:
        response = client.batches.create(data=operations)
        logging.debug("Got batch response: %s", response)
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating batch request:\n%s\nAborting.", err_resp)
        raise
    else:
        return response  # should contain operation_id if we later need this


def add_members_to_lists(client, csv_members=PATH_ADD_MEMBERS, batch=False, created_lists=None):
    """Add members to list. Update if they are already there.

    Parse data from csv (default /data/in/tables/add_members.csv)
    """
    logging.info("Adding members to list as described in %s", csv_members)
    serialized_data = serialize_members_input(csv_members, created_lists)
    no_members = len(serialized_data)
    logging.info("Detected %s members to be added.", no_members)

    if no_members <= BATCH_THRESHOLD or not batch:
        _add_members_serial(client, serialized_data)
    else:
        batch_response = _add_members_in_batch(client, serialized_data)


def run_update_lists(client, params):
    """Run the writer only updating tables
    """
    update_lists(
        client,
        csv_lists=params.get('update_lists',
                             PATH_UPDATE_LISTS))

def create_lists_add_members(client):
    """Run the writer create tables and add members

    Take input tables for
        - creating lists
        - adding-or-updating members in list(s)
    and parse them in that order.

    """

    created_lists = create_lists(client)
    add_members_to_lists(client, created_lists=created_lists)


def run():
    try:
        client, params, tables = set_up(path_config='/data/')
        run_writer(client, params, tables)
    except ValueError as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(err, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)


def run_writer(client, params, tables):
    """Analyze which tables are defined and act accordingly

    Three combinations of input files are possible:

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
    if len(tablenames) == 0:
        raise ValueError("No input tables specified!")
    if PATH_UPDATE_LISTS in tablenames:
        update_lists(client)
    elif PATH_NEW_LISTS in tablenames:
        if len(tablenames) == 1:
            create_lists(client=client)
        elif len(tablenames) == 2 and PATH_ADD_MEMBERS in tablenames:
            create_lists_add_members(client)
        else:
            raise ValueError("Not sure what to do, got these tables: {}".format(tables))
    elif 'add_members.csv' in tablenames and len(tablenames) == 1:
        add_members_to_lists(client=client)
    else:
        raise ValueError("Not sure what to do, got these tables: {}".format(tables))
    logging.info("Writer finished")
