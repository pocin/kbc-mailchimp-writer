import pytest

from mcwriter.utils import (_clean_mandatory_custom_fields,
                            # clean_and_validate_members_data,
                            members_mandatory_custom_fields)

def test_cleaning_mandatory_custom_fields_raises_if_not_present():
    data = {
        "email_address": "Robin@example.com",
    }

    with pytest.raises(KeyError):
        _clean_mandatory_custom_fields(data, members_mandatory_custom_fields)


def test_cleaning_mandatory_custom_fields_validates_correctly():
    data = {
        "email_address": "Robin@example.com",
        "status": "subscribed"
    }

    expected ={
        "email_address": "Robin@example.com",
        "status": "subscribed"
    }

    assert _clean_mandatory_custom_fields(data, members_mandatory_custom_fields) == expected


def test_cleaning_mandatory_custom_fields_raises_if_invalid():
    data = {
        "email_address": "Robin@example.com",
        "status": "INCORRECT STATUS"
    }

    with pytest.raises(TypeError):
        _clean_mandatory_custom_fields(data, members_mandatory_custom_fields)
