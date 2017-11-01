"""Utilities for mailchimp writer

@author robin@keboola.com
"""
from collections import defaultdict
import csv
import os
import json
import time
import logging
from mailchimp3 import MailChimp
from requests import HTTPError, ConnectionError
from .cleaning import (clean_and_validate_lists_data,
                       clean_and_validate_members_data,
                       clean_and_validate_members_delete_data,
                       clean_and_validate_tags_data)
from .exceptions import CleaningError, ConfigError, MissingFieldError
BATCH_POLLING_DELAY = 10 #seconds
CHUNK_SIZE = 500 #rows

def serialize_dotted_path_dict(cleaned_flat_data, delimiter='__'):
    """Convert fields from csv file into required nested format

    Handles only nesting one level deep

    When creating a new mailing list, the POST data contains nested fields. In
    the input csv, the nesting is marked with `delimiter` ('contacts#address')

    Arguments:
        flat_data (dict): A dict where keys possibly contain dotted path
    Returns:
        A nested representation of the flat dict.
    """
    serialized = defaultdict(dict)

    for key, value in cleaned_flat_data.items():
        if delimiter in key:
            lvl1, lvl2 = key.split(delimiter, maxsplit=1)
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


def serialize_members_input(path, action, created_lists=None, chunk_size=CHUNK_SIZE):
    """Parse the members csvfile containing subscribers and lists

    optionally (created_lists arg) appends the list_id to the data based on the
    custom_id and custom_list_id mapping defined in csv

    Args:
        path (str): /path/to/inputs/add_members.csv
        created_lists (dict): Mapping of custom_list_id: actual mailchimp list_id

    Returns:
        a list of serialized dicts in a format that can be used by MC Api

    """
    actions = ('add_or_update', 'update', 'delete')
    if action not in actions:
        raise ConfigError("When serializing members data, you must choose one"
                          "of the following actions {}, not {}".format(
                              actions, action))
    with open(path, 'r') as lists:
        reader = csv.DictReader(lists)
        while reader:
            serialized = []
            for _ in range(chunk_size):
                try:
                    line = next(reader)
                except StopIteration:
                    break
                else:
                    if created_lists:
                        mailchimp_list_id = created_lists[line.pop('custom_list_id')]
                        line['list_id'] = mailchimp_list_id
                    if action in {'add_or_update', 'update'}:
                        cleaned_flat_data = clean_and_validate_members_data(line)
                    else:
                        # it's delete
                        cleaned_flat_data = clean_and_validate_members_delete_data(line)

                    serialized_line = serialize_dotted_path_dict(cleaned_flat_data)
                    serialized.append(serialized_line)
            # make sure there are no leftovers
            if len(serialized) == 0:
                raise StopIteration
            yield serialized

def serialize_tags_input(path_csv, created_lists=None):
    """Parse the csv file for adding tags to existing list
    Args:
        path_csv (str): 'path/to/members.csv'
        created_lists (dict): a mapping of custom_list_ids to real
            (newly created) mailchimp lists. If you do not supply this,
            it is assumed, that you provided list_id in the csv.

    Returns:
        a list of dicts containing cleaned and serialized data
    """
    serialized = []
    with open(path_csv, 'r') as tags:
        reader = csv.DictReader(tags)
        for line in reader:
            if created_lists:
                mailchimp_list_id = created_lists[line.pop('custom_list_id')]
                line['list_id'] = mailchimp_list_id
            cleaned_flat = clean_and_validate_tags_data(line)
            serialized_line = serialize_dotted_path_dict(cleaned_flat)
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

def prepare_batch_data_delete_members(serialized_data):
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
        'method': 'DELETE',
        'path': '/lists/{list_id}/members/{subscriber_hash}',
        'operation_id': None
    }
    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['path'] = temp['path'].format(
            list_id=data.pop('list_id'),
            subscriber_hash=data.pop('subscriber_hash'))
        temp['operation_id'] = data['email_address']
        operations.append(temp)
    return {'operations': operations}

def prepare_batch_data_update_members(serialized_data):
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
        'method': 'PATCH',
        'path': '/lists/{list_id}/members/{subscriber_hash}',
        'operation_id': None,
        'body': None}
    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['path'] = temp['path'].format(
            list_id=data.pop('list_id'),
            subscriber_hash=data.pop('subscriber_hash'))
        temp['operation_id'] = data['email_address']
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
    client_config = {'enabled': enabled,
                     'mc_user': ""} # empty string is ok for username
    try:
        client_config['mc_secret'] = params['#apikey']
    except KeyError:
        raise MissingFieldError(
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
            raise ConfigError("Invalid credentials. Check them and try again.")
        else:
            raise
    except ConnectionError:
        raise ConfigError("Invalid credentials. Check them and try again.")
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
    logging.info("Waiting for batch operation %s to finish", batch_id)
    while batch_still_pending(batch_status):
        batch_status = client.batches.get(batch_id)
        time.sleep(api_delay)
    else:
        logging.info("Batch %s finished.\n"
                     "total_operations: %s\n"
                     "erorred_opeartions: %s\n"
                     "finished_opeartions: %s\n",
                     batch_status['id'],
                     batch_status['total_operations'],
                     batch_status['errored_operations'],
                     batch_status['finished_operations'])
        return batch_status

def write_batches_to_csv(batches, outpath, bucketname='in.c-mailchimp-writer'):
    fieldnames = [col for col in batches[0].keys() if col != '_links']
    with open(outpath, 'w') as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        for batch in batches:
            del batch['_links']
            writer.writerow(batch)
    manifest = {
        'destination': bucketname + '.' + os.path.splitext(os.path.basename(outpath))[0]
    }
    manipath = outpath+'.manifest'
    with open(manipath, 'w') as f:
        json.dump(manifest, f)
    return outpath, manipath
