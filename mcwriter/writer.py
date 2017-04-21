"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
import datetime
import json
from keboola import docker
from mailchimp3 import MailChimp
from requests import HTTPError
from .utils import (serialize_new_lists_input,
                    prepare_batch_data)

# valid fields for creating mailing list according to
# https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists
PATH_NEW_LISTS = '/data/in/tables/new_lists.csv'
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
        client_config['mc_secret'] = params['apikey']
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
    operation_id = 'create_lists_{:%Y%m%d:%H-%M-%S}'.format(
        datetime.datetime.now())
    logging.debug('Creating lists in batch mode: operation_id %s', operation_id)
    operation_template = {
        'method': 'POST',
        'path': '/lists',
        'operation_id': operation_id,
        'body': None}

    operations = prepare_batch_data(operation_template, serialized_data)
    try:
        response = client.batches.create(data=operations)
        logging.debug("batch_id = %s", json.loads(response.text))
    except HTTPError as exc:
        err_resp = json.loads(exc.response.text)
        logging.error("Error while creating request:\n%s\nAborting.", err_resp)
        sys.exit(1)

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
    serialized_data = serialize_new_lists_input(csv_lists)
    logging.debug("Creating %d new lists defined in %s", len(serialized_data), csv_lists)
    if batch or len(serialized_data) > BATCH_THRESHOLD:
        _create_lists_in_batch(client=client, serialized_data=serialized_data)
    else:
        _create_lists_serial(client=client, serialized_data=serialized_data)
    logging.info("New lists created.")


def update_list():
    """Update existing mailing list"""
    pass
