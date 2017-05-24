import pytest
from mcwriter.exceptions import MissingFieldError
from mcwriter.cleaning import clean_and_validate_tags_data

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

def test_cleaning_tags_some_additional_fields():
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
