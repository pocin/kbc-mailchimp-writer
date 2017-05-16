"""
Testing helper functions for cleaning different field types
"""
import pytest
from mcwriter.exceptions import CleaningError, ConfigError, MissingFieldError
from mcwriter.cleaning import (_clean_mandatory_str_fields,
                               _clean_optional_str_fields,
                               _clean_mandatory_bool_fields,
                               _clean_optional_bool_fields,
                               _clean_optional_custom_fields,
                               _clean_exclusive_fields,
                               lists_mandatory_str_fields,
                               lists_optional_str_fields,
                               lists_mandatory_bool_fields,
                               lists_optional_bool_fields,
                               lists_optional_custom_fields)


def test_cleaning_mandatory_str_fields_success():
    data = {
        "name": "Robin",
        "contact__company": "Nemeth",
        "contact__address1": "Bar Bar 42",
        "contact__city": "Foocity",
        "contact__state": "LalaLand",
        "contact__zip": "666",
        "contact__country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults__from_name": "Me",
        "campaign_defaults__from_email": "Me@you.together",
        "campaign_defaults__subject": "Hi",
        "campaign_defaults__language": "id",
    }

    expected_data = {}
    expected_data.update(data)

    cleaned_data = _clean_mandatory_str_fields(data, lists_mandatory_str_fields)
    assert cleaned_data == expected_data


def test_cleaning_mandatory_str_fields_missing_fails():
    data = {
        # "name": "Robin",
        "contact__company": "Nemeth",
        "contact__address1": "Bar Bar 42",
        "contact__city": "Foocity",
        "contact__state": "LalaLand",
        "contact__zip": "666",
        "contact__country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults__from_name": "Me",
        "campaign_defaults__from_email": "Me@you.together",
        "campaign_defaults__subject": "Hi",
        "campaign_defaults__language": "id",
    }

    with pytest.raises(MissingFieldError):
        cleaned_data = _clean_mandatory_str_fields(data, lists_mandatory_str_fields)

def test_cleaning_mandatory_str_fields_missing_fails_dtype():
    data = {
        "name": 12345,
        "contact__company": "Nemeth",
        "contact__address1": "Bar Bar 42",
        "contact__city": "Foocity",
        "contact__state": "LalaLand",
        "contact__zip": "666",
        "contact__country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults__from_name": "Me",
        "campaign_defaults__from_email": "Me@you.together",
        "campaign_defaults__subject": "Hi",
        "campaign_defaults__language": "id",
    }

    with pytest.raises(CleaningError):
        cleaned_data = _clean_mandatory_str_fields(data, lists_mandatory_str_fields)

def test_cleaning_optional_str_fields_missing_doesnt_raise():
    data = {
        "name": "Robin",
        "contact__company": "Nemeth",
        "contact__address2": "Foobar",
        "contact__phone": None,
        "notify_on_subscribe": '',
    }
    expected = {
        "name": "Robin",
        "contact__company": "Nemeth",
        "contact__address2": "Foobar",
        "contact__phone": '',
        "notify_on_subscribe": '',
    }
    assert expected ==_clean_optional_str_fields(data, lists_optional_str_fields)

def test_cleaning_optional_str_fields_missing_raises_wrong_dtype():
    data = {
        "contact__address2": 12345,
    }

    with pytest.raises(CleaningError):
        _clean_optional_str_fields(data, lists_optional_str_fields)

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

    with pytest.raises(MissingFieldError):
        _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields)


def test_cleaning_mandatory_bool_field_not_bool_raises():
    data = {
        "name": "Robin",
        "email_type_option": "One does simply not convert this to bool"
    }

    with pytest.raises(CleaningError):
        _clean_mandatory_bool_fields(data, lists_mandatory_bool_fields)


def test_cleaning_optional_bool_fields_not_bool_raises():
    data = {
        "name": "Robin",
        "use_archive_bar": "One does simply not convert this to bool"
    }

    with pytest.raises(CleaningError):
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
    with pytest.raises(CleaningError):
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
    with pytest.raises(CleaningError):
        _clean_optional_custom_fields(data, lists_optional_custom_fields)

def test_clean_exclusive_fields_works():
    data = {'foo': 1,
            'bar': 1}
    exclusive_fields = set(['foo', 'qux'])
    expected = data
    cleaned = _clean_exclusive_fields(data, exclusive_fields)
    assert cleaned == expected


def test_clean_exclusive_fields_raises_if():
    data = {'foo': 1,
            'bar': 1}
    exclusive_fields = set(['foo', 'bar'])
    with pytest.raises(CleaningError):
        _clean_exclusive_fields(data, exclusive_fields)
