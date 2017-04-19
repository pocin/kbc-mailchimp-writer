"""
Keboola mailchimp writer

@author robin@keboola.com
"""

import sys
import logging
from keboola import docker
from mailchimp3 import MailChimp
from requests import HTTPError
import csv

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


def create_list():
    """Create new mailing list"""
    logging.debug("Creating new lists defined in {}".format(PATH_NEW_LISTS))
    with open(PATH_NEW_LISTS, 'r') as lists:
        reader = csv.DictReader(lists)
        for line in reader:
            serialized = 

def update_list():
    """Update existing mailing list"""
    pass

