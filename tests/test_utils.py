import pytest
import json
from tempfile import NamedTemporaryFile
from mailchimp3 import MailChimp
from unittest.mock import Mock
import requests
from mcwriter.utils import (serialize_dotted_path_dict,
                            serialize_lists_input,
                            serialize_members_input,
                            prepare_batch_data_lists,
                            prepare_batch_data_add_members,
                            _setup_client,
                            _verify_credentials,
                            batch_still_pending,
                            wait_for_batch_to_finish)

@pytest.fixture
def finished_batch_response():
    return {
        '_links': [{'href': 'https://us15.api.mailchimp.com/3.0/batches',
                    'method': 'GET',
                    'rel': 'parent',
                    'schema': 'https://us15.api.mailchimp.com/schema/3.0/CollectionLinks/Batches.json',
                    'targetSchema': 'https://us15.api.mailchimp.com/schema/3.0/Definitions/Batches/CollectionResponse.json'},
                   {'href': 'https://us15.api.mailchimp.com/3.0/batches/a3bb03520b',
                    'method': 'GET',
                    'rel': 'self',
                    'targetSchema': 'https://us15.api.mailchimp.com/schema/3.0/Definitions/Batches/Response.json'},
                   {'href': 'https://us15.api.mailchimp.com/3.0/batches/a3bb03520b',
                    'method': 'DELETE',
                    'rel': 'delete'}],
        'completed_at': '2017-04-21T11:08:22+00:00',
        'errored_operations': 1,
        'finished_operations': 2,
        'id': 'a3bb03520b',
        'response_body_url': 'https://mailchimp-api-batch.s3.amazonaws.com/a3bb03520b-response.tar.gz?AWSAccessKeyId=AKIAJWOH5BECJQZIEWNQ&Expires=1492773508&Signature=Z2WnBzKxILiuOqW%2FGHa66IqRhM8%3D',
        'status': 'finished',
        'submitted_at': '2017-04-21T11:08:15+00:00',
        'total_operations': 3}

@pytest.fixture
def pending_batch_response():
    return {
        '_links': [{'href': 'https://us15.api.mailchimp.com/3.0/batches',
                    'method': 'GET',
                    'rel': 'parent',
                    'schema': 'https://us15.api.mailchimp.com/schema/3.0/CollectionLinks/Batches.json',
                    'targetSchema': 'https://us15.api.mailchimp.com/schema/3.0/Definitions/Batches/CollectionResponse.json'},
                   {'href': 'https://us15.api.mailchimp.com/3.0/batches/a3bb03520b',
                    'method': 'GET',
                    'rel': 'self',
                    'targetSchema': 'https://us15.api.mailchimp.com/schema/3.0/Definitions/Batches/Response.json'},
                   {'href': 'https://us15.api.mailchimp.com/3.0/batches/a3bb03520b',
                    'method': 'DELETE',
                    'rel': 'delete'}],
        'id': 'a3bb03520b',
        'response_body_url': 'https://mailchimp-api-batch.s3.amazonaws.com/a3bb03520b-response.tar.gz?AWSAccessKeyId=AKIAJWOH5BECJQZIEWNQ&Expires=1492773508&Signature=Z2WnBzKxILiuOqW%2FGHa66IqRhM8%3D',
        'status': 'pending',
        'submitted_at': '2017-04-21T11:08:15+00:00',
        'total_operations': 3}

def test_serializing_new_lists():
    flat = {'name': 'Robin',
            'contact.address': 'Foobar',
            'contact.country': 'Czechia',
            'confirm': True}
    expected = {
        'name': 'Robin',
        'contact': {
            'address': 'Foobar',
            'country': 'Czechia'},
        'confirm': True}
    serialized = serialize_dotted_path_dict(flat)
    assert expected == serialized


def test_serializing_new_lists_input_csv(new_lists_csv):
    # Fake inputs
    serialized = serialize_lists_input(new_lists_csv.name)

    expected = [{'campaign_defaults': {'from_email': 'dark_mage001@email.com',
                                       'from_name': 'Albus Dumlbedore',
                                       'language': 'English',
                                       'subject': 'Welcome, young wizard!'},
                 'contact': {'address1': '4 Privet Drive',
                             'address2': '',
                             'city': 'Wizardshire',
                             'company': 'Magical company ltd.',
                             'country': 'Wonderland',
                             'phone': '',
                             'state': 'Wonderland',
                             'zip': '66678'},
                 'email_type_option': True,
                 'name': 'Wizards of the world',
                 'notify_on_subscribe': '',
                 'notify_on_unsubscribe': '',
                 'permission_reminder': 'You are in this list, because you just turned 11 and have magical abilities',
                 'use_archive_bar': False,
                 'custom_id': 'custom_list1',
                 'visibility': 'prv'},
                # Same as the first one, but all 'a' are switched to 'xx'
                {'campaign_defaults': {'from_email': 'dxxrk_mxxge001@emxxil.com',
                                       'from_name': 'XXlbus Dumlbedore',
                                       'language': 'English',
                                       'subject': 'Welcome, young wizxxrd!'},
                 'contact': {'address1': '4 Privet Drive',
                             'address2': '',
                             'city': 'Wizxxrdshire',
                             'company': 'Mxxgicxxl compxxny ltd.',
                             'country': 'Wonderlxxnd',
                             'phone': '',
                             'state': 'Wonderlxxnd',
                             'zip': '66678'},
                 'email_type_option': True,
                 'name': 'Wizxxrds of the world',
                 'notify_on_subscribe': '',
                 'notify_on_unsubscribe': '',
                 'permission_reminder': 'You xxre in this list, becxxuse you just turned 11 xxnd hxxve mxxgicxxl xxbilities',
                 'use_archive_bar': False,
                 'custom_id': 'custom_list2',
                 'visibility': 'prv'},
                ]


    assert expected[0] == serialized[0]
    assert expected[1] == serialized[1]


def test_preparing_batch_data():
    data = [{'name':'bar', 'baz':'qux'},
            {'name':'bar2', 'baz': 'quxx'}]

    batch_data = prepare_batch_data_lists(data)

    expected = {'operations': [
        {'method': 'POST',
         'path': '/lists',
         'operation_id': 'bar',
         'body': json.dumps({'name':'bar', 'baz':'qux'})},
        {'method': 'POST',
         'path': '/lists',
         'operation_id': 'bar2',
         'body': json.dumps({'name':'bar2', 'baz': 'quxx'})}
    ]}
    assert batch_data == expected

def test_serializing_members_input(new_members_csv):
    serialized = serialize_members_input(new_members_csv.name)
    expected = [
        {'email_address': 'robin@keboola.com',
         'list_id': '12345', # comes from the csvfile
         'vip': True,
         'interests' : {
             '1234abc': True,
             'abc1234': True},
         'status': 'subscribed',
         'status_if_new': 'subscribed',
         'email_type': True,
         'subscriber_hash': 'a2a362ca5ce6dc7e069b6f7323342079',  #md5 hash
         'merge_fields': {'*|FNAME|*': 'Robin'},
        },
        {'email_address': 'foo@bar.com',
         'list_id': '12345',
         'vip': False,
         'interests' : {
             '1234abc': True,
             'abc1234': False},
         'status': 'pending',
         'status_if_new': 'subscribed',
         'subscriber_hash': 'f3ada405ce890b6f8204094deb12d8a8',  #md5 hash
         'email_type': False,
         'merge_fields': {'*|FNAME|*': ''},
        }
    ]
    assert serialized[0] == expected[0]
    assert serialized[1] == expected[1]

def test_serializing_members_input_linked_to_lists(new_members_csv_linked_to_lists,
                                                   created_lists):
    serialized = serialize_members_input(
        new_members_csv_linked_to_lists.name,
        created_lists=created_lists)
    expected = [
        {'email_address': 'robin@keboola.com',
         'list_id': 'mailchimp_list_id', # the id comes from the mapping returned by create_lists()
         'vip': True,
         'interests' : {
             '1234abc': True,
             'abc1234': True},
         'status': 'subscribed',
         'status_if_new': 'subscribed',
         'email_type': True,
         'subscriber_hash': 'a2a362ca5ce6dc7e069b6f7323342079',  #md5 hash
         'merge_fields': {'*|FNAME|*': 'Robin'},
        },
        {'email_address': 'foo@bar.com',
         'list_id': 'mailchimp_list_id', 
         'vip': False,
         'interests' : {
             '1234abc': True,
             'abc1234': False},
         'status': 'pending',
         'status_if_new': 'subscribed',
         'subscriber_hash': 'f3ada405ce890b6f8204094deb12d8a8',  #md5 hash
         'email_type': False,
         'merge_fields': {'*|FNAME|*': ''},
        }
    ]
    assert serialized == expected


def test_preparing_batch_members_data():
    data = [{'foo':'bar', 'email_address': 'foo@barbar.cz',
             'list_id':'ab1234', 'subscriber_hash': 'foobar',
             'status_if_new': 'subscribed'},
            {'foo':'bar2', 'email_address': 'foo@bar.cz',
             'list_id':'ab1234', 'subscriber_hash': 'foobar',
             'status_if_new': 'subscribed'}]

    batch_data = prepare_batch_data_add_members(data)

    expected = {'operations': [
        {'method': 'PUT',
         'path': '/lists/ab1234/members/foobar',
         'operation_id': 'foo@barbar.cz',
         'status_if_new': 'subscribed',
         'body': json.dumps({'foo':'bar', 'email_address': 'foo@barbar.cz'})},
        {'method': 'PUT',
         'path': '/lists/ab1234/members/foobar',
         'operation_id': 'foo@bar.cz',
         'status_if_new': 'subscribed',
         'body': json.dumps({'foo':'bar2', 'email_address': 'foo@bar.cz'})}
    ]}
    assert batch_data == expected

def test_setting_up_client_works(monkeypatch):
    params = {'#apikey': 'secret'}
    client = _setup_client(params, enabled=False)
    assert isinstance(client, MailChimp)


def test_setting_up_client_fails_on_nonpresent_apikey(monkeypatch):
    params = {}
    with pytest.raises(KeyError):
        client = _setup_client(params, enabled=False)


def test_veryifying_credentials_fails_on_wrong_apikey(client, monkeypatch):
    def raise_http_error():
        err = requests.HTTPError("WRONG!")
        class Resp:
            status_code = 401
        err.response = Resp()
        raise err

    monkeypatch.setattr(client.api_root, 'get', raise_http_error)
    with pytest.raises(ValueError) as excinfo:
        _verify_credentials(client)
    excinfo.match('Invalid credentials')


def test_veryifying_credentials_wrong_apikey_ConnectionError(client, monkeypatch):
    def raise_ConnectionError():
        raise requests.ConnectionError("WRONG!")

    monkeypatch.setattr(client.api_root, 'get', raise_ConnectionError)
    with pytest.raises(ValueError) as excinfo:
        _verify_credentials(client)
    excinfo.match('Invalid credentials')

def test_checking_status_of_batch_operation(pending_batch_response,
                                            finished_batch_response):
    assert batch_still_pending(pending_batch_response) is True
    assert batch_still_pending(finished_batch_response) is False

def test_waiting_for_batch_op_to_finish(pending_batch_response,
                                        finished_batch_response,
                                        monkeypatch):

    fake_client_get_batch_id = Mock(
        side_effect=[pending_batch_response, finished_batch_response])
    monkeypatch.setattr('mailchimp3.mailchimpclient.MailChimpClient._get',
                        fake_client_get_batch_id)

    client = MailChimp('foo', 'bar')
    batch_id = 'a3bb03520b'
    results = wait_for_batch_to_finish(client, batch_id, api_delay=0.1)
    assert results == finished_batch_response

