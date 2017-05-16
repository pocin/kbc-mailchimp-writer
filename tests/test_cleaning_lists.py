import pytest
from mcwriter.cleaning import clean_and_validate_lists_data

def test_cleaning_and_validating_lists_data():
    """Just one complete example to try the parent function"""

    data = {
        # mandatory str fields
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
        # optional str fields
        "contact__address2": "ADDRESS 2",
        "contact__phone": "telephone",
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
        # optional str fields
        "contact__address2": "ADDRESS 2",
        "contact__phone": "telephone",
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


def test_cleaning_lists_raises_if_custom_id_and_list_id():
    one_list = {'custom_id': 'alist123', 'list_id': 'hash12foo34'}
    with pytest.raises(ValueError):
        clean_and_validate_lists_data(one_list)

def test_cleaning_lists_raises_if_mandatory_str_field_is_missing():
    one_list = {
        # mandatory str fields
        "name": "Robin",
        # wrong name, should be contact#support
        "contact_company": "Nemeth",
        "contact_address1": "Bar Bar 42",
        "contact_city": "Foocity",
        "contact_state": "LalaLand",
        "contact.zip": "666",
        "contact.country": "Ohyea",
        "permission_reminder": "You want this!",
        "campaign_defaults.from_name": "Me",
        "campaign_defaults.from_email": "Me@you.together",
        "campaign_defaults.subject": "Hi",
        "campaign_defaults.language": "id",
        # optional str fields
        "contact__address2": "ADDRESS 2",
        "contact__phone": "telephone",
        "notify_on_subscribe": "mail@example.com",
        "notify_on_unsubscribe": "mail@example.com",
        # optional bool
        "use_archive_bar": 'true',
        # mandatory bool
        "email_type_option": 'false',
        # optional custom fields
        "visibility": 'prv'
    }
    with pytest.raises(KeyError):
        clean_and_validate_lists_data(one_list)
