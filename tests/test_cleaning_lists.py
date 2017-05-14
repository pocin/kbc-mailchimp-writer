import pytest
from mcwriter.cleaning import clean_and_validate_lists_data

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


def test_cleaning_lists_raises_if_custom_id_and_list_id():
    one_list = {'custom_id': 'alist123', 'list_id': 'hash12foo34'}
    with pytest.raises(ValueError):
        clean_and_validate_lists_data(one_list)
