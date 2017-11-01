import logging
import re
from hashlib import md5
from .exceptions import CleaningError, MissingFieldError

# fields for adding lists
lists_mandatory_str_fields = ("name", "contact__company", "contact__address1",
                              "contact__city", "contact__state", "contact__zip",
                              "contact__country", "permission_reminder",
                              "campaign_defaults__from_name",
                              "campaign_defaults__from_email",
                              "campaign_defaults__subject",
                              "campaign_defaults__language")
lists_optional_str_fields = ("contact__address2", "contact__phone",
                             "notify_on_subscribe", "notify_on_unsubscribe",
                             "custom_id")
lists_mandatory_bool_fields = ("email_type_option", )
lists_optional_bool_fields = ("use_archive_bar", )
lists_optional_custom_fields = {"visibility": ['pub', 'prv']}
lists_exclusive_fields = set(('list_id', 'custom_id'))
# fields for adding members
members_mandatory_str_fields = ('email_address', 'list_id')
members_optional_custom_fields = {"status": ['subscribed', 'unsubscribed',
                                              'cleaned', 'pending',
                                              'transactional'],
                                   "status_if_new": ['subscribed', 'unsubscribed',
                                                     'cleaned', 'pending',
                                                     'transactional']}


members_mandatory_bool_fields = tuple()
members_optional_str_fields = ('language', 'custom_list_id' )
members_optional_bool_fields = ("vip", "email_type")
members_exclusive_fields = set(('list_id', 'custom_list_id'))

# fields for adding tags
tags_optional_bool_fields = ('required', 'public')
tags_mandatory_str_fields = ('name', )
tags_optional_str_fields = ('tag', 'default_value', 'help_text')
tags_optional_integer_fields = ('display_order', )
tags_mandatory_custom_fields = {'type': ["text", "number", "address", "phone",
                                         "date", "url", "imageurl", "radio",
                                         "dropdown", "birthday", "zip"]}
tags_exclusive_fields = set(('list_id', 'custom_id'))


def clean_and_validate_lists_data(one_list):
    logging.debug("Cleaning one mailing list data")

    for cleaning_procedure, fields in (
            (_clean_exclusive_fields, lists_exclusive_fields),
            (_clean_mandatory_bool_fields, lists_mandatory_bool_fields),
            (_clean_mandatory_str_fields, lists_mandatory_str_fields ),
            (_clean_optional_str_fields, lists_optional_str_fields),
            (_clean_optional_bool_fields, lists_optional_bool_fields),
            (_clean_optional_custom_fields, lists_optional_custom_fields)):
        one_list = cleaning_procedure(one_list, fields)
    return one_list

def _hash_email(email):
    return md5(bytes(email, 'utf-8')).hexdigest()

def clean_and_validate_members_data(line):
    logging.debug("Cleaning members data")
    for cleaning_procedure, fields in (
            (_clean_exclusive_fields, members_exclusive_fields),
            (_clean_optional_str_fields, members_optional_str_fields),
            (_clean_optional_bool_fields, members_optional_bool_fields),
            (_clean_mandatory_bool_fields, members_mandatory_bool_fields),
            (_clean_mandatory_str_fields, members_mandatory_str_fields),
            (_clean_optional_custom_fields, members_optional_custom_fields)):
        line = cleaning_procedure(line, fields)
    line = _clean_members_interests(line)
    line['subscriber_hash'] = _hash_email(line['email_address'])
    return line

def clean_and_validate_members_delete_data(line):
    logging.debug("Cleaning members data for deleting")
    line = _clean_mandatory_str_fields(line, ['list_id', 'email_address'])
    line['subscriber_hash'] = _hash_email(line['email_address'])
    return line


def clean_and_validate_tags_data(one_tag):
    logging.debug("Cleaning tags data")
    for cleaning_procedure, fields in (
            (_clean_exclusive_fields, tags_exclusive_fields),
            (_clean_optional_bool_fields, tags_optional_bool_fields),
            (_clean_mandatory_str_fields, tags_mandatory_str_fields),
            (_clean_optional_str_fields, tags_optional_str_fields),
            (_clean_optional_integer_fields, tags_optional_integer_fields),
            (_clean_mandatory_custom_fields, tags_mandatory_custom_fields)):
        one_tag = cleaning_procedure(one_tag, fields)
    one_tag = _clean_tags_options(one_tag)
    return one_tag


def _clean_mandatory_str_fields(one_list, fields):
    for field in fields:
        try:
            value = one_list[field]
        except KeyError:
            raise MissingFieldError(
                "Every entry must have str '{}' field.\n"
                "This entry doesnt: {}".format(field, one_list))
        else:
            if not isinstance(value, str):
                raise CleaningError(
                    "Field '{}:{}' must be a string! It is '{}'".format(
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
                raise CleaningError("The string field '{}' is non-mandatory,"
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
            raise MissingFieldError(
                "Every list must have boolean '{}' field."
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
                raise CleaningError(
                    "Can't convert mandatory '{}' field to boolean."
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
                raise CleaningError(
                    "Can't convert optional '{}' field to boolean. "
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
        try:
            value = one_list[field]
        except KeyError:
            # nothing to clean here
            pass
        else:
            if value not in expected:
                raise CleaningError(
                    "The field {field} must be one of "
                    "{expected}. It is {value} in {data}".format(
                        field=field,
                        expected=expected, value=value, data=one_list))
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
            raise MissingFieldError(
                "Every member must have boolean '{}' field. "
                "This entry doesnt: {}".format(field, one_list))
        if value not in expected:
            raise CleaningError(
                "The field '{field}' must be one of "
                "{expected}. It is '{value}' in {data}".format(
                    field=field,
                    expected=expected, value=value, data=one_list))
    return one_list


def _clean_members_interests(one_list):
    interests_pattern = r'^interests__[0-9a-zA-Z]+$'
    pattern = re.compile(interests_pattern)
    interests = []

    for field in (f for f in one_list if f.startswith('interests')):
        if not pattern.match(field):
            raise CleaningError(
                "'interests' columns must have format '{}'"
                "not '{}'".format(interests_pattern, field))
        else:
            interests.append(field)
    return _clean_optional_bool_fields(one_list, interests)


def _clean_members_merge_fields(one_list):
    merge_field_pat = r'^merge_fields__\w+$'
    pattern = re.compile(merge_field_pat)
    ok_fields = []

    for field in (f for f in one_list if f.startswith('merge_fields')):
        if not pattern.match(field):
            raise CleaningError("'merge_fields' columns must have format '{}'"
                             "not '{}'".format(merge_field_pat, field))
        else:
            ok_fields.append(field)
    return _clean_optional_str_fields(one_list, ok_fields)

def _clean_exclusive_fields(one_list, exclusive_fields):
    """
    Validate that the data doesn't contain both fields
    """
    if exclusive_fields.issubset(set(one_list)):
        # both exclusive fields are there!
        raise CleaningError(
            "It doesn't make sense to provide both {} in the row '{}'."
            "Check the documentation for usage.".format(
                exclusive_fields, one_list))
    else:
        return one_list

def _clean_optional_integer_fields(one_record, fields):
    for field in fields:
        try:
            one_record[field] = int(one_record[field])
        except KeyError:
            # the field is optional, we do not care!
            pass
        except ValueError:
            raise CleaningError("Field {} in record {} must be integer,"
                                " not '{}'".format(field, one_record,
                                                   type(one_record[field])))
    return one_record

def _clean_tags_options(one_record):
    option_field_pat = r'^options__$'
    pattern = re.compile(option_field_pat)
    ok_fields = []

    for field in (f for f in one_record if f.startswith('options__')):
        if field in ['options__phone_format', 'options__date_format']:
            one_record[field]= str(one_record[field])
        elif field in ['options__default_country', 'options__size']:
            try:
                one_record[field]= int(one_record[field])
            except ValueError:
                raise CleaningError("The field {} in record {}"
                                    "must be integer, not {}".format(
                                        field, one_record[field],
                                        type(one_record[field])))
        elif field == 'options__choices':
            one_record[field] = list(map(lambda x: str(x).strip(),
                                         one_record[field].split(';')))

    return one_record
