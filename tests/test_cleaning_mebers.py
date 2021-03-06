import pytest

from mcwriter.exceptions import MissingFieldError, CleaningError
from mcwriter.cleaning import (_clean_mandatory_custom_fields,
                               clean_and_validate_members_data,
                               _clean_members_interests,
                               _clean_exclusive_fields,
                               _clean_members_merge_fields)

def test_cleaning_mandatory_custom_fields_raises_if_not_present():
    data = {
        "email_address": "Robin@example.com",
    }

    with pytest.raises(MissingFieldError):
        _clean_mandatory_custom_fields(data, {'required_field': ['possible value 1', 'possible_value 2']})


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

    assert _clean_mandatory_custom_fields(data,
                                          {'status': ['subscribed', 'unsubscribed'],
                                           'status_if_new':['subscribed', 'unsubscribed']}) == expected


def test_cleaning_mandatory_custom_fields_raises_if_invalid():
    data = {
        "email_address": "Robin@example.com",
        "status": "INCORRECT STATUS",
        'status_if_new': 'subscribed',

    }

    with pytest.raises(CleaningError):
        _clean_mandatory_custom_fields(data, {'status': ['subscribed'], 'status_if_new': ['subscribed']})


def test_cleaning_members_data_all_options_succeeds():
    data = {
        'email_address': 'Robin@example.com',
        'list_id': '12345',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests__abc1234': 'true',
        'interests__abc1235': 'false'
        }
    expected = {
        'email_address': 'Robin@example.com',
        'list_id': '12345',
        'status': 'subscribed',
        'status_if_new': 'subscribed',
        'vip': True,
        'email_type': True,
        'language': 'en',
        'interests__abc1234': True,
        'interests__abc1235': False,
        'subscriber_hash': 'd3c17ef52c397921a87c1de66f2311c2'}

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
        'interests__abc1_234': 'true'
        }

    with pytest.raises(CleaningError):
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
        'interests__abc1234': 'true'
        }

    with pytest.raises(MissingFieldError):
        clean_and_validate_members_data(data)


def test_cleaning_members_data_all_options_raises_on_missing_email():
    data = {
        'status': 'subscribed',
        'vip': 'true',
        'email_type': 'true',
        'language': 'en',
        'interests__abc1__234': 'true'
        }

    with pytest.raises(MissingFieldError):
        clean_and_validate_members_data(data)

def test_cleaning_members_data_all_options_raises_on_missing_status():
    data = {
        'vip': 'true',
        'email_address': 'foo@bar.cz',
        'email_type': 'true',
        'language': 'en',
        'interests__abc1234': 'true',
        'list_id': 'foo'
        }

    with pytest.raises(MissingFieldError):
        clean_and_validate_members_data(data)

def test_cleaning_members_interests_cleans_ok():
    data = {
        'email_address': 'robin@keboola.com',
        'interests__abc1234': 'true',
    }

    expected = {
        'email_address': 'robin@keboola.com',
        'interests__abc1234': True,
    }
    assert _clean_members_interests(data) == expected


def test_cleaning_members_interests_raises_on_invalid_interest():
    data = {
        'email_address': 'robin@keboola.com',
        'interests__abc1 234': 'true', # the space is reduntant
    }

    with pytest.raises(CleaningError):
        _clean_members_interests(data)


def test_cleaning_members_merge_fields_cleans_ok():
    data = {
        'email_address': 'robin@keboola.com',
        'merge_fields__FNAME': 'Robin',
        'merge_fields__LNAME': 'Nemeth',
    }

    expected = {
        'email_address': 'robin@keboola.com',
        'merge_fields__FNAME': 'Robin',
        'merge_fields__LNAME': 'Nemeth',
    }
    assert _clean_members_merge_fields(data) == expected


def test_providing_custom_list_id_and_list_id_raises():
    data = {
        'email_address': 'robin@keboola.com',
        'custom_list_id': 'foobar',
        'list_id': '123abc',
    }
    exclusive_fields = {'custom_list_id', 'list_id'}
    with pytest.raises(CleaningError):
        _clean_exclusive_fields(data, exclusive_fields)
