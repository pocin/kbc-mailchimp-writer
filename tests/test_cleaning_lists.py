import pytest
from mcwriter.cleaning import (_clean_mandatory_str_fields,
                               _clean_optional_str_fields,
                               _clean_mandatory_bool_fields,
                               _clean_optional_bool_fields,
                               _clean_optional_custom_fields,
                               clean_and_validate_lists_data,
                               lists_mandatory_str_fields,
                               lists_optional_str_fields,
                               lists_mandatory_bool_fields,
                               lists_optional_bool_fields,
                               lists_optional_custom_fields)

def test_cleaning_mandatory_str_fields_success():
    data = {
        "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address1": "Bar Bar 42",
        "contact.city": "Foocity",
        "contact.state": "LalaLand",
        "contact.zip": "666",
        "contact.country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults.from_name": "Me",
        "campaign_defaults.from_email": "Me@you.together",
        "campaign_defaults.subject": "Hi",
        "campaign_defaults.language": "id",
    }

    expected_data = {}
    expected_data.update(data)

    cleaned_data = _clean_mandatory_str_fields(data, lists_mandatory_str_fields)
    assert cleaned_data == expected_data


def test_cleaning_mandatory_str_fields_missing_fails():
    data = {
        # "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address1": "Bar Bar 42",
        "contact.city": "Foocity",
        "contact.state": "LalaLand",
        "contact.zip": "666",
        "contact.country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults.from_name": "Me",
        "campaign_defaults.from_email": "Me@you.together",
        "campaign_defaults.subject": "Hi",
        "campaign_defaults.language": "id",
    }

    with pytest.raises(KeyError):
        cleaned_data = _clean_mandatory_str_fields(data, lists_mandatory_str_fields)

def test_cleaning_optional_str_fields_missing_doesnt_raise():
    data = {
        "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address2": "Foobar",
        "contact.phone": None,
        "notify_on_subscribe": '',
    }
    expected = {
        "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address2": "Foobar",
        "contact.phone": '',
        "notify_on_subscribe": '',
    }
    assert expected ==_clean_optional_str_fields(data, lists_optional_str_fields)

def test_cleaning_mandatory_bool_field_is_there():
    data = {
        "name": "Robin",
        "email_type_option": "TrUe"
    }

    expected = {
        "name": "Robin",
        "email_type_option": True
    }
    assert _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields) == expected


def test_cleaning_mandatory_bool_field_handling_None():
    data = {
        "name": "Robin",
        "email_type_option": None
    }

    expected = {
        "name": "Robin",
        "email_type_option": False
    }
    assert _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields) == expected

def test_cleaning_mandatory_bool_field_not_there_raises():
    data = {
        "name": "Robin",
    }

    with pytest.raises(KeyError):
        _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields)


def test_cleaning_mandatory_bool_field_not_bool_raises():
    data = {
        "name": "Robin",
        "email_type_option": "One does simply not convert this to bool"
    }

    with pytest.raises(TypeError):
        _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields)


def test_cleaning_optional_bool_fields_not_bool_raises():
    data = {
        "name": "Robin",
        "use_archive_bar": "One does simply not convert this to bool"
    }

    with pytest.raises(TypeError):
        _clean_optional_bool_fields(data, lists_optional_bool_fields)


def test_cleaning_optional_bool_fields_true():
    data = {
        "name": "Robin",
        "use_archive_bar": "True"
    }

    expected = {
        "name": "Robin",
        "use_archive_bar": True
    }
    assert _clean_optional_bool_fields(data, lists_optional_bool_fields) == expected

def test_cleaning_optional_bool_fields_false():
    data = {
        "name": "Robin",
        "use_archive_bar": "false"
    }

    expected = {
        "name": "Robin",
        "use_archive_bar": False
    }
    assert _clean_optional_bool_fields(data, lists_optional_bool_fields) == expected


def test_cleaning_optional_bool_fields2_raises_on_empty_string():
    data = {
        "name": "Robin",
        "use_archive_bar": ""
    }
    with pytest.raises(TypeError):
        _clean_optional_bool_fields(data, lists_optional_bool_fields)


def test_cleaning_optional_bool_fields_None():
    data = {
        "name": "Robin",
        "use_archive_bar": None
    }

    expected = {
        "name": "Robin",
        "use_archive_bar": False
    }
    assert _clean_optional_bool_fields(data, lists_optional_bool_fields) == expected

def test_optional_custom_fields_prv():
    data = {
        "name": "Robin",
        "visibility": 'prv'
    }
    expected = {
        "name": "Robin",
        "visibility": 'prv'
    }

    assert _clean_optional_custom_fields(data, lists_optional_custom_fields) == expected


def test_optional_custom_fields_pub():
    data = {
        "name": "Robin",
        "visibility": 'pub'
    }
    expected = {
        "name": "Robin",
        "visibility": 'pub'
    }
    assert _clean_optional_custom_fields(data, lists_optional_custom_fields) == expected

def test_clean_optional_custom_fields_raises_unconvertable():
    data = {
        "name": "Robin",
        "visibility": 'Must be pub or prv!'
    }
    with pytest.raises(TypeError):
        _clean_optional_custom_fields(data, lists_optional_custom_fields)


def test_cleaning_and_validating_lists_data():
    """Just one complete example to try the parent function"""

    data = {
        # mandatory str fields
        "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address1": "Bar Bar 42",
        "contact.city": "Foocity",
        "contact.state": "LalaLand",
        "contact.zip": "666",
        "contact.country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults.from_name": "Me",
        "campaign_defaults.from_email": "Me@you.together",
        "campaign_defaults.subject": "Hi",
        "campaign_defaults.language": "id",
        # optional str fields
        "contact.address2": "ADDRESS 2",
        "contact.phone": "telephone",
        "notify_on_subscribe": "mail@example.com",
        "notify_on_unsubscribe": "mail@example.com",
        # optional bool
        "use_archive_bar": 'true',
        # mandatory bool
        "email_type_option": 'false',
        # optional custom fields
        "visibility": 'prv'
    }
    expected_data = {
        # mandatory str fields
        "name": "Robin",
        "contact.company": "Nemeth",
        "contact.address1": "Bar Bar 42",
        "contact.city": "Foocity",
        "contact.state": "LalaLand",
        "contact.zip": "666",
        "contact.country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults.from_name": "Me",
        "campaign_defaults.from_email": "Me@you.together",
        "campaign_defaults.subject": "Hi",
        "campaign_defaults.language": "id",
        # optional str fields
        "contact.address2": "ADDRESS 2",
        "contact.phone": "telephone",
        "notify_on_subscribe": "mail@example.com",
        "notify_on_unsubscribe": "mail@example.com",
        # optional bool
        "use_archive_bar": True,
        # mandatory bool
        "email_type_option": False,
        # optional custom fields
        "visibility": 'prv'
    }
    cleaned_data = clean_and_validate_lists_data(data)
    assert cleaned_data == expected_data
