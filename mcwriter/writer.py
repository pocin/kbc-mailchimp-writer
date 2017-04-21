"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
import datetime
from keboola import docker
from mailchimp3 import MailChimp
from requests import HTTPError
from .utils import (serialize_new_lists_input,
                    prepare_batch_data)

# valid fields for creating mailing list according to
# https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json
# http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists
PATH_NEW_LISTS = '/data/in/tables/new_lists.csv'

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

def show_lists(client):
    """Show existing mailing lists"""
    pass


def create_lists(client, csv_lists=PATH_NEW_LISTS, batch=False):
    """Create new mailing list """
    serialized_data = serialize_new_lists_input(csv_lists)
    logging.debug("Creating {count} new lists defined in {path}".format(
        count=len(serialized_data),
        path=csv_lists))

    if batch or len(serialized_data) > 5:
        operation_id = 'batch_create_lists_{:%Y%m%d:%H-%M-%S}'.format(
            datetime.datetime.now())
        logging.debug('Creating lists in batch mode: operation_id {}'.format(
            operation_id))
        operation_template = {
            'method': 'POST',
            'path': '/lists',
            'operation_id': operation_id,
            'body': None}

        operations = prepare_batch_data(operation_template, serialized_data)
        try:
            client.batches.create(data=operations)
        except HTTPError as e:
            err_resp = json.loads(e.response.text)
            logging.error("Error while creating request:\n{}\nAborting.".format(err_resp))
            sys.exit(1)
    else:
        logging.debug('Creating lists in serial.')
        for data in serialized_data:
            try:
                client.lists.create(data=data)
            except HTTPError as e:
                err_resp = json.loads(e.response.text)
                logging.error("Error while creating request:\n"
                              "POST data:\n{}"
                              "Error message\n{}".format(data, err_resp))
                sys.exit(1)
    logging.info("New lists created.")


def update_list():
    """Update existing mailing list"""
    pass
