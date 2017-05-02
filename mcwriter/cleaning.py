import logging
import re
from hashlib import md5

# fields for adding lists
lists_mandatory_str_fields = ("name", "contact.company", "contact.address1",
                              "contact.city", "contact.state", "contact.zip",
                              "contact.country", "permission_reminder",
                              "campaign_defaults.from_name",
                              "campaign_defaults.from_email",
                              "campaign_defaults.subject",
                              "campaign_defaults.language")
lists_optional_str_fields = ("contact.address2", "contact.phone",
                             "notify_on_subscribe", "notify_on_unsubscribe",
                             "custom_id")
lists_mandatory_bool_fields = ("email_type_option", )
lists_optional_bool_fields = ("use_archive_bar", )
lists_optional_custom_fields = {"visibility": ['pub', 'prv']}

# fields for adding members
members_mandatory_str_fields = ('email_address', 'list_id')
members_mandatory_custom_fields = {"status": ['subscribed', 'unsubscribed',
                                              'cleaned', 'pending',
                                              'transactional'],
                                   "status_if_new": ['subscribed', 'unsubscribed',
                                                     'cleaned', 'pending',
                                                     'transactional']}


members_mandatory_bool_fields = tuple()
members_optional_str_fields = ('language', 'custom_list_id' )
members_optional_bool_fields = ("vip", "email_type")


def clean_and_validate_lists_data(one_list):
    logging.debug("Cleaning one mailing list data")

    if 'custom_id' in one_list and 'list_id' in one_list:
        raise ValueError("You can't have both `custom_list_id` and `list_id` at "
                         "the same time in your new_lists.csv")

    for cleaning_procedure, fields in (
            (_clean_mandatory_bool_fields, lists_mandatory_bool_fields),
            (_clean_optional_str_fields, lists_optional_str_fields),
            (_clean_optional_bool_fields, lists_optional_bool_fields),
            (_clean_optional_custom_fields, lists_optional_custom_fields)):
        one_list = cleaning_procedure(one_list, fields)
    return one_list


def clean_and_validate_members_data(one_list):
    logging.debug("Cleaning members data")
    for cleaning_procedure, fields in (
            (_clean_optional_str_fields, members_optional_str_fields),
            (_clean_optional_bool_fields, members_optional_bool_fields),
            (_clean_mandatory_bool_fields, members_mandatory_bool_fields),
            (_clean_mandatory_str_fields, members_mandatory_str_fields),
            (_clean_mandatory_custom_fields, members_mandatory_custom_fields)):
        one_list = cleaning_procedure(one_list, fields)
    one_list = _clean_members_interests(one_list)
    md5hash = md5(bytes(one_list['email_address'], 'utf-8')).hexdigest()
    one_list['subscriber_hash'] = md5hash
    return one_list


def _clean_mandatory_str_fields(one_list, fields):
    for field in fields:
        try:
            value = one_list[field]
        except KeyError:
            raise KeyError(
                "Every entry must have str {} field. This entry doesnt: {}".format(
                field, one_list))
        else:
            if not isinstance(value, str):
                raise TypeError("Field {}:{} must be a string! It is {}".format(
                    field, value, type(value)))
    return one_list

def _clean_optional_str_fields(one_list, fields):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """
    for field in fields:
        try:
            if one_list[field] is None:
                one_list[field] = ''
            if not isinstance(one_list[field], str):
                raise TypeError("The string field '{}' is non-mandatory,"
                                " but must be a string if present. "
                                "Now it is '{}' in {}".format(
                                    field, type(one_list[field]), one_list))
        except KeyError:
            # Doesnt matter, the optional field isnt there.
            continue
    return one_list

def _clean_mandatory_bool_fields(one_list, fields):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """
    for field in fields:
        try:
            # The csv can contain a string, True/False, or None (if empty)
            # neither None, nor empty strings are not allowed
            # For the api, we need to turn strings that appear as true/false into
            # python True/False dtypes
            value_clean = one_list[field].lower()
        except KeyError:
            raise KeyError("Every list must have boolean '{}' field."
                           " This entry doesnt: '{}'".format(field, one_list))
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

def _clean_optional_bool_fields(one_list, fields):
    """Clean and validate fields

    Args:
        one_list (dict): one mailing list details in a dict format
    """

    for field in fields:
        try:
            # The csv can contain a string, True/False, or None (if empty)
            # neither None, nor empty strings are not allowed
            # For the api, we need to turn strings that appear as true/false into
            # python True/False dtypes
            value_clean = one_list[field].lower()
        except KeyError:
            continue
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


def _clean_optional_custom_fields(one_list, fields):
    """Clean and validate fields. Do not raise if field is not present

    Args:
        one_list (dict): one mailing list details in a dict format
        fields (dict): Mapping of column name and possible values in an list
    """
    for field, expected in fields.items():
        value = one_list[field]
        if value not in expected:
            raise TypeError("The field {field} must be one of "
                            "{expected}. It is {value} in {data}".format(
                                field=field,
                                expected=expected,
                                value=value,
                                data=one_list))
    return one_list


def _clean_mandatory_custom_fields(one_list, fields):
    """Clean and validate fields. Raise if the field is not present

    Args:
        one_list (dict): one mailing list details in a dict format
        fields (dict): Mapping of column name and possible values in an list
    """
    for field, expected in fields.items():
        try:
            value = one_list[field]
        except KeyError:
            raise KeyError("Every member must have boolean '{}' field. "
                           "This entry doesnt: {}".format(field, one_list))
        if value not in expected:
            raise TypeError("The field '{field}' must be one of "
                            "{expected}. It is '{value}' in {data}".format(
                                field=field,
                                expected=expected,
                                value=value,
                                data=one_list))
    return one_list


def _clean_members_interests(one_list):
    pattern = re.compile(r'^interests\.[0-9a-zA-Z]+$')
    interests = []

    for field in (f for f in one_list if f.startswith('interests')):
        if not pattern.match(field):
            raise ValueError("'interests' columns must have format 'interests.[0-9a-zA-Z]+'"
                             "not '{}'".format(field))
        else:
            interests.append(field)
    return _clean_optional_bool_fields(one_list, interests)


def _clean_members_merge_fields(one_list):
    pattern = re.compile(r'^merge_fields\.\*\|\w+\|\*$')
    ok_fields = []

    for field in (f for f in one_list if f.startswith('merge_fields')):
        if not pattern.match(field):
            raise ValueError("'merge_fields' columns must have format 'merge_fields.*|<tagName>|*'"
                             "not '{}'".format(field))
        else:
            ok_fields.append(field)
    return _clean_optional_str_fields(one_list, ok_fields)

