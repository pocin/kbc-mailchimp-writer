import pytest
from mcwriter.exceptions import MissingFieldError, CleaningError
from mcwriter.cleaning import clean_and_validate_tags_data, _clean_tags_options

def test_cleaning_tags_minimal_example():
    data = {
        'name': 'My custom tag',
        'type': 'text',
    }

    expected = data
    cleaned = clean_and_validate_tags_data(data)
    assert cleaned == expected

def test_cleaning_tags_missing_required_field():
    data = {
        'name': 'My custom tag',
    }

    expected = data
    with pytest.raises(MissingFieldError):
        clean_and_validate_tags_data(data)

def test_cleaning_tags_invalid_type():
    data = {
        'name': 'My custom tag',
        'type': 'qux',
    }

    with pytest.raises(CleaningError):
        clean_and_validate_tags_data(data)

def test_cleaning_tags_optional_bool_fields():
    data = {
        'name': 'My custom tag',
        'type': 'text',
        'required': 'true'
    }
    expected =  {
        'name': 'My custom tag',
        'type': 'text',
        'required': True
    }

    cleaned = clean_and_validate_tags_data(data)
    assert cleaned == expected

def test_cleaning_tags_optional_str_fields():
    data = {
        'name': 'My custom tag',
        'type': 'text',
        'tag': 'MYTAG'
    }
    expected =  {
        'name': 'My custom tag',
        'type': 'text',
        'tag': 'MYTAG'
    }

    cleaned = clean_and_validate_tags_data(data)
    assert cleaned == expected

def test_cleaning_tags_integer_fields():
    data = {
        'name': 'My custom tag',
        'type': 'text',
        'display_order': '2'
    }

    expected = {
        'name': 'My custom tag',
        'type': 'text',
        'display_order': 2
    }

    cleaned = clean_and_validate_tags_data(data)
    assert cleaned == expected


def test_cleaning_tags_integer_fields_fails_on_wrong_dtype():
    data = {
        'name': 'My custom tag',
        'type': 'text',
        'display_order': 'foo'
    }

    with pytest.raises(CleaningError):
        clean_and_validate_tags_data(data)

def test_cleaning_tags_options_cleaning_int():
    data = {
        'options__default_country':'3',
    }
    expected = {
        'options__default_country': 3
    }

    cleaned = _clean_tags_options(data)
    assert cleaned == expected

def test_cleaning_tags_options_cleaning_int_wring_type():
    data = {
        'options__default_country': 'xxx',
    }
    with pytest.raises(CleaningError):
        _clean_tags_options(data)

def test_cleaning_tags_options():
    data = {
        'options__default_country': 'xxx',
        'options__default_country': 'xxx',
        'options__default_country': 'xxx',
        'options__default_country': 'xxx',
    }
