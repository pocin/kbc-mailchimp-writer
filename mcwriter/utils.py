"""Utilities for mailchimp writer

@author robin@keboola.com
"""
from collections import defaultdict
import csv
import json
from keboola import docker


def serialize_dotted_path_dict(flat_data):
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

    for key, value in flat_data.items():
        try:
            # The csv can contain a number, True/False, or None (if empty)
            value_clean = value.lower()
        except AttributeError:
            value_clean = value
        if '.' in key:
            lvl1, lvl2 = key.split('.', maxsplit=1)
            if value_clean == 'false':
                serialized[lvl1][lvl2] = False
            elif value_clean == 'true':
                serialized[lvl1][lvl2] = True
            else:
                serialized[lvl1][lvl2] = value

        else:
            if value_clean == 'false':
                serialized[key] = False
            elif value_clean == 'true':
                serialized[key] = True
            else:
                serialized[key] = value

    return serialized

def serialize_new_lists_input(path):
    """Parse the inputs csvfile containing details on new mailing lists

    Arguments:
        path (str): /path/to/inputs/new_lists.csvfile
    Returns:
        a list of serialized dicts in a format that can be used by MC Api
    """
    serialized = []
    with open(path, 'r') as lists:
        reader = csv.DictReader(lists)
        for line in reader:
            serialized_line = serialize_dotted_path_dict(line)
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
        temp['body'] = data
        operations.append(temp)

    return operations

