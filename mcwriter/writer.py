"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
import datetime
import json
import time
from keboola import docker
from mailchimp3 import MailChimp
from requests import HTTPError
from .utils import (serialize_lists_input,
                    serialize_members_input,
                    prepare_batch_data_lists,
                    prepare_batch_data_add_members)

# valid fields for creating mailing list according to
# https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists
PATH_NEW_LISTS = '/data/in/tables/new_lists.csv'
PATH_UPDATE_LISTS = '/data/in/tables/update_lists.csv'
PATH_UPDATE_MEMBERS = '/data/in/tables/update_members.csv'
PATH_ADD_MEMBERS = '/data/in/tables/add_members.csv'
BATCH_THRESHOLD = 3 # When to switch from serial jobs to batch jobs

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
    if params.get('debug'):
        logging.basicConfig(level=logging.DEBUG)

    client = _setup_client(params)
    return client


def _setup_client(params):
    """Set up mailchimp client using supplied credentials

    Also verify that username and apikey are provided in json config
    """
    client_config = {}
    try:
        client_config['mc_user'] = params['username']
    except KeyError:
        logging.error("Please provide your mailchimp username")
        sys.exit(1)
    try:
        client_config['mc_secret'] = params['#apikey']
    except KeyError:
        logging.error("Please provide your mailchimp apikey")
        sys.exit(1)

    client = MailChimp(**client_config)
    # try a simple request if credentials are ok
    logging.info("Validating credentials")
    try:
        client.api_root.get()
    except HTTPError as err:
        if err.response.status_code == 401:
            logging.error("Invalid credentials. Check them and try again.")
            sys.exit(1)
        else:
            raise
    else:
        logging.info("Credentials OK")
        return client

def show_lists():
    """Show existing mailing lists"""
    pass

def _create_lists_in_batch(client, serialized_data):
    operations = prepare_batch_data_lists(serialized_data)
    try:
        response = client.batches.create(data=operations)
        logging.debug("Got batch response: %s", response)
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating request:\n%s\nAborting.", err_resp)
        sys.exit(1)
    else:
        return response  # should contain operation_id if we later need this

def _create_lists_serial(client, serialized_data):
    logging.debug('Creating lists in serial.')
    for data in serialized_data:
        try:
            client.lists.create(data=data)
        except HTTPError as exc:
            err_resp = json.loads(exc.response.text)
            logging.error("Error while creating request:\n"
                          "POST data:\n%s"
                          "Error message\n%s", data, err_resp)
            sys.exit(1)

def create_lists(client, csv_lists=PATH_NEW_LISTS, batch=False):
    """Create new mailing list """
    serialized_data = serialize_lists_input(csv_lists)
    logging.debug("Creating %d new lists defined in %s", len(serialized_data), csv_lists)
    if batch or len(serialized_data) > BATCH_THRESHOLD:
        batch_response = _create_lists_in_batch(client=client, serialized_data=serialized_data)
        # The batch job is executed in the background on the MC servers
        # To check the status, we need to GET /3.0/batches/{batch_response['id']}
    else:
        _create_lists_serial(client=client, serialized_data=serialized_data)
    logging.info("New lists created.")


def update_lists(client, csv_lists=PATH_UPDATE_LISTS):
    """Update existing mailing lists

    the input csv file should have the same structure as for lists creation
    with an additional column `list_id` used to reference existing lists.
    """
    serialized_data = serialize_lists_input(csv_lists)
    logging.debug("Updating %d new lists defined in %s", len(serialized_data), csv_lists)
    _update_lists_serial(client=client, serialized_data=serialized_data)
    logging.info("Lists updated.")

    # TODO add batch operations maybe?

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
        sys.exit(1)
    else:
        return response  # should contain operation_id if we later need this


def add_members_to_lists(client, csv_members=PATH_ADD_MEMBERS, batch=False):
    """Add members to list. Update if they are already there.

    Parse data from csv (default /data/in/tables/add_members.csv)
    """
    logging.info("Adding members to list as described in %s", csv_members)
    serialized_data = serialize_members_input(csv_members)
    no_members = len(serialized_data)
    logging.info("Detected %s members to be added.", no_members)

    if no_members <= BATCH_THRESHOLD or not batch:
        _add_members_serial(client, serialized_data)
    else:
        batch_response = _add_members_in_batch(client, serialized_data)
