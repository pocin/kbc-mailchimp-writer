"""Utilities for mailchimp writer

@author robin@keboola.com
"""
from collections import defaultdict
import csv
import json
from .cleaning import (clean_and_validate_lists_data,
                       clean_and_validate_members_data)


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


def serialize_members_input(path):
    """Parse the members csvfile containing subscribers and lists

    Args:
        path (str): /path/to/inputs/add_members.csv

    Returns:
        a list of serialized dicts in a format that can be used by MC Api
    """
    serialized = []
    with open(path, 'r') as lists:
        reader = csv.DictReader(lists)
        for line in reader:
            cleaned_flat_data = clean_and_validate_members_data(line)
            serialized_line = serialize_dotted_path_dict(cleaned_flat_data)
            serialized.append(serialized_line)
    return serialized

def prepare_batch_data(template, serialized_data):
    """Prepare data for batch operation

    When submitting batch operation, the data should contain the target for the
    request (the template), a request method and the payload. This function
    copies the data into the template for each datadict

    Args:
        template (dict): common data for all operations (method, path)
        serialized_data (lists): a list structures (dicts) containing the
            payload

    """
    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['body'] = json.dumps(data)
        operations.append(temp)

    return {'operations': operations}

def prepare_batch_data_add_members(template, serialized_data):
    """Prepare data for batch operation

    When submitting batch operation, the data should contain the target for the
    request (the template), a request method and the payload. This function
    copies the data into the template for each datadict

    Args:
        template (dict): common data for all operations (method, path)
        serialized_data (lists): a list structures (dicts) containing the
            payload

    """
    operations = []

    for data in serialized_data:
        temp = template.copy()
        temp['body'] = json.dumps(data)
        temp['path'] = temp['path'].format(serialized_data['list_id'])
        operations.append(temp)

    return {'operations': operations}
