"""Utilities for mailchimp writer

@author robin@keboola.com
"""
from collections import defaultdict
import csv
import json
import logging
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

def clean_and_validate_lists_data(one_list):
    logging.debug("Cleaning one mailing list data")
    for cleaning_procedure in (_clean_mandatory_bool_fields,
                               _clean_optional_str_fields,
                               _clean_mandatory_bool_fields,
                               _clean_optional_bool_fields,
                               _clean_optional_custom_fields):
        one_list = cleaning_procedure(one_list)
    return one_list



def _clean_mandatory_str_fields(one_list):
    mandatory_str_fields = {
        "name": str,
        "contact.company": str,
        "contact.address1": str,
        "contact.city": str,
        "contact.state": str,
        "contact.zip": str,
        "contact.country": str,
        "permission_reminder": str,
        "campaign_defaults.from_name": str,
        "campaign_defaults.from_email": str,
        "campaign_defaults.subject": str,
        "campaign_defaults.language": str,
    }
    for field in mandatory_str_fields:
        try:
            value = one_list[field]
            if not isinstance(value, str):
                raise TypeError("Field {}:{} must be a string! It is {}".format(
                    field, value, type(value)))
        except KeyError:
            raise KeyError(
                "Every list must have str %s field. This entry doesnt: %s",
                field, one_list)
    return one_list

def _clean_optional_str_fields(one_list):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """
    optional_str_fields = {
        "contact.address2": str,
        "contact.phone": str,
        "notify_on_subscribe": str,
        "notify_on_unsubscribe": str,
    }
    for field in optional_str_fields:
        try:
            if one_list[field] is None:
                one_list[field] = ''
                if not isinstance(one_list[field], str):
                    raise TypeError("The string field {} is non-mandatory,"
                                    " but must be a string if present. "
                                    "Now it is {} in {}".format(
                                        field, type(one_list[field]), one_list))
        except KeyError:
            # Doesnt matter, the optional field isnt there.
            continue
    return one_list

def _clean_mandatory_bool_fields(one_list):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """
    mandatory_bool_fields = {"email_type_option": bool}
    for field in mandatory_bool_fields:
        try:
            # The csv can contain a string, True/False, or None (if empty)
            # neither None, nor empty strings are not allowed
            # For the api, we need to turn strings that appear as true/false into
            # python True/False dtypes
            value_clean = one_list[field].lower()
        except KeyError:
            raise KeyError("Every list must have boolean {} field."
                           " This entry doesnt: {}".format(field, one_list))
        except AttributeError:
            # it is None, True, or False
            one_list[field] = bool(one_list[field])
        else:
            if value_clean == 'false':
                one_list[field] = False
            elif value_clean == 'true':
                one_list[field] = True
            else:
                raise TypeError("Can't convert mandatory '{}' field to boolean."
                                "Make sure it is either 'true' or 'false',"
                                " not '{}'".format(field, one_list[field]))
    return one_list

def _clean_optional_bool_fields(one_list):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """

    optional_bool_fields = {"use_archive_bar": bool}
    for field in optional_bool_fields:
        try:
            # The csv can contain a string, True/False, or None (if empty)
            # neither None, nor empty strings are not allowed
            # For the api, we need to turn strings that appear as true/false into
            # python True/False dtypes
            value_clean = one_list[field].lower()
        except AttributeError:
            # it is None, True, or False
            one_list[field] = bool(one_list[field])
        else:
            if value_clean == 'false':
                one_list[field] = False
            elif value_clean == 'true':
                one_list[field] = True
            else:
                raise TypeError("Can't convert optional '{}' field to boolean. "
                                "Make sure it is either 'true' or 'false',"
                                " not '{}'".format(field, one_list[field]))
    return one_list


def _clean_optional_custom_fields(one_list):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """
    optional_custom_fields = {"visibility": ['pub', 'prv']}
    for field, expected in optional_custom_fields.items():
        value = one_list[field]
        if value not in expected:
            raise TypeError("The field {field} must be one of "
                            "{expected}. It is {value} in {data}".format(
                                field=field,
                                expected=expected,
                                value=value,
                                data=one_list))
    return one_list


def serialize_lists_input(path):
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
            cleaned_flat_data = clean_and_validate_lists_data(line)
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

