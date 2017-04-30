import pytest

from mcwriter.cleaning import (_clean_mandatory_custom_fields,
                               clean_and_validate_members_data,
                               _clean_members_interests,
                               _clean_members_merge_fields,
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
        "status": "subscribed",
        "status_if_new": "subscribed"
    }

    expected ={
        "email_address": "Robin@example.com",
        "status": "subscribed",
        "status_if_new": "subscribed"
    }

    assert _clean_mandatory_custom_fields(data, members_mandatory_custom_fields) == expected


def test_cleaning_mandatory_custom_fields_raises_if_invalid():
    data = {
        "email_address": "Robin@example.com",
        "status": "INCORRECT STATUS",
        'status_if_new': 'subscribed',

    }

    with pytest.raises(TypeError):
        _clean_mandatory_custom_fields(data, members_mandatory_custom_fields)


def test_cleaning_members_data_all_options_succeeds():
    data = {
        'email_address': 'Robin@example.com',
        'list_id': '12345',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests.abc1234': 'true',
        'interests.abc1235': 'false'
        }
    expected = {
        'email_address': 'Robin@example.com',
        'list_id': '12345',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        'vip': True,
        'email_type': True,
        'language': 'en',
        'interests.abc1234': True,
        'interests.abc1235': False,
        'subscriber_hash': '582b00d27bcf92a600f0d5e0f12be026'}

    assert clean_and_validate_members_data(data) == expected

def test_cleaning_members_data_all_options_raises_on_invalid_interest_id():
    data = {
        'email_address': 'Robin@example.com',
        'list_id': '1234',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests.abc1#234': 'true'
        }

    with pytest.raises(ValueError):
        clean_and_validate_members_data(data)

def test_cleaning_members_data_all_options_raises_on_missing_list_id():
    data = {
        'email_address': 'Robin@example.com',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        # Missing list_id
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests.abc1234': 'true'
        }

    with pytest.raises(KeyError):
        clean_and_validate_members_data(data)

def test_cleaning_members_data_all_options_raises_on_missing_email():
    data = {
        'status': 'subscribed',
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests.abc1#234': 'true'
        }

    with pytest.raises(KeyError):
        clean_and_validate_members_data(data)


def test_cleaning_members_interests_cleans_ok():
    data = {
        'email_address': 'robin@keboola.com',
        'interests.abc1234': 'true',
    }

    expected = {
        'email_address': 'robin@keboola.com',
        'interests.abc1234': True,
    }
    assert _clean_members_interests(data) == expected


def test_cleaning_members_interests_raises_on_invalid_interest():
    data = {
        'email_address': 'robin@keboola.com',
        'interests.abc1 234': 'true', # the space is reduntant
    }

    with pytest.raises(ValueError):
        _clean_members_interests(data)


def test_cleaning_members_merge_fields_cleans_ok():
    data = {
        'email_address': 'robin@keboola.com',
        'merge_fields.*|FNAME|*': 'Robin',
        'merge_fields.*|LNAME|*': 'Nemeth',
    }

    expected = {
        'email_address': 'robin@keboola.com',
        'merge_fields.*|FNAME|*': 'Robin',
        'merge_fields.*|LNAME|*': 'Nemeth',
    }
    assert _clean_members_merge_fields(data) == expected


def test_cleaning_members_merge_fields_raises_on_invalid_syntax():
    data = {
        'email_address': 'robin@keboola.com',
        'merge_fields.*|FNAME*|': 'Robin',
    }

    with pytest.raises(ValueError):
        _clean_members_merge_fields(data)
