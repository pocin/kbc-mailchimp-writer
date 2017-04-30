"""Utilities for mailchimp writer

@author robin@keboola.com
"""
from collections import defaultdict
import csv
import json
import time
import logging
from mailchimp3 import MailChimp
from requests import HTTPError
from .cleaning import (clean_and_validate_lists_data,
                       clean_and_validate_members_data)
BATCH_POLLING_DELAY = 5 #seconds

def serialize_dotted_path_dict(cleaned_flat_data):
    """Convert fields from csv file into required nested format

    Handles only nesting one level deep

    When creating a new mailing list, the POST data contains nested fields. In
    the input csv, the nesting is marked with dotted path ('contacts.address')

    Arguments:
        flat_data (dict): A dict where keys possibly contain dotted path
    Returns:
        A nested representation of the flat dict.
    """
    serialized = defaultdict(dict)

    for key, value in cleaned_flat_data.items():
        if '.' in key:
            lvl1, lvl2 = key.split('.', maxsplit=1)
            serialized[lvl1][lvl2] = value
        else:
            serialized[key] = value

    return serialized

def serialize_lists_input(path):
    """Parse the inputs csvfile containing details on new mailing lists

    Arguments:
        path (str): /path/to/inputs/new_lists.csv
    Returns:
        a list of serialized dicts in a format that can be used by MC Api
    """
    serialized = []
    with open(path, 'r') as lists:
        reader = csv.DictReader(lists)
        for line in reader:
            cleaned_flat_data = clean_and_validate_lists_data(line)
            serialized_line = serialize_dotted_path_dict(cleaned_flat_data)
            serialized.append(serialized_line)
    return serialized


def serialize_members_input(path, created_lists=None):
    """Parse the members csvfile containing subscribers and lists

    optionally (created_lists arg) appends the list_id to the data based on the
    custom_id and custom_list_id mapping defined in csv

    Args:
        path (str): /path/to/inputs/add_members.csv
        created_lists (dict): Mapping of custom_list_id: actual mailchimp list_id

    Returns:
        a list of serialized dicts in a format that can be used by MC Api

    """
    serialized = []
    with open(path, 'r') as lists:
        reader = csv.DictReader(lists)
        for line in reader:
            cleaned_flat_data = clean_and_validate_members_data(line)
            if created_lists:
                mailchimp_list_id = created_lists[cleaned_flat_data.pop('custom_list_id')]
                cleaned_flat_data['list_id'] = mailchimp_list_id
            serialized_line = serialize_dotted_path_dict(cleaned_flat_data)
            serialized.append(serialized_line)
    return serialized

def prepare_batch_data_lists(serialized_data):
    """Prepare data for batch operation

    When submitting batch operation, the data should contain the target for the
    request (the template), a request method and the payload. This function
    copies the data into the template for each datadict

    Args:
        template (dict): common data for all operations (method, path)
        serialized_data (lists): a list structures (dicts) containing the
            payload

    """
    template = {
        'method': 'POST',
        'path': '/lists',
        'operation_id': None,
        'body': None}

    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['operation_id'] = data['name']
        temp['body'] = json.dumps(data)
        operations.append(temp)

    return {'operations': operations}

def prepare_batch_data_add_members(serialized_data):
    """Prepare data for batch operation

    When submitting batch operation, the data should contain the target for the
    request (the template), a request method and the payload. This function
    copies the data into the template for each datadict

    Args:
        template (dict): common data for all operations (method, path)
        serialized_data (lists): a list structures (dicts) containing the
            payload

    """
    template = {
        'method': 'PUT',
        'path': '/lists/{list_id}/members/{subscriber_hash}',
        'operation_id': None,
        'status_if_new': None,
        'body': None}
    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['path'] = temp['path'].format(
            list_id=data.pop('list_id'),
            subscriber_hash=data.pop('subscriber_hash'))
        temp['operation_id'] = data['email_address']
        temp['status_if_new'] = data.pop('status_if_new')
        temp['body'] = json.dumps(data)
        operations.append(temp)

    return {'operations': operations}


def _setup_client(params, enabled=True):
    """Set up mailchimp client using supplied credentials

    Also verify that username and apikey are provided in json config
    Args:
        enabled (bool): for testing purposes, leave to True in prod env.
    """
    client_config = {'enabled': enabled}
    try:
        client_config['mc_user'] = params['username']
    except KeyError:
        raise KeyError("Please provide your mailchimp username")
    try:
        client_config['mc_secret'] = params['#apikey']
    except KeyError:
        raise KeyError(
            "Please provide your mailchimp apikey in #encrypted format")

    client = MailChimp(**client_config)
    client = _verify_credentials(client)
    return client

def _verify_credentials(client):
    logging.info("Validating credentials")
    try:
        client.api_root.get()
    except HTTPError as err:
        if err.response.status_code == 401:
            raise ValueError("Invalid credentials. Check them and try again.")
        else:
            raise
    else:
        logging.info("Credentials OK")
        return client

def batch_still_pending(batch_response):
    if batch_response['status'] == 'finished':
        return False
    else:
        return True


def wait_for_batch_to_finish(client, batch_id, api_delay=BATCH_POLLING_DELAY):
    batch_status = client.batches.get(batch_id)
    while batch_still_pending(batch_status):
        batch_status = client.batches.get(batch_id)
        time.sleep(api_delay)
    else:
        logging.info("Batch %s finished.\n"
                     "total_operations: %s"
                     "erorred_opeartions: %s",
                     batch_status['id'],
                     batch_status['total_operations'],
                     batch_status['finished_operations'])
        return batch_status
