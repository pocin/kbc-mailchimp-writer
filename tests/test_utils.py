"""
Test utility functions

"""
from unittest.mock import Mock
import csv
import json
import requests
import pytest
from mailchimp3 import MailChimp
from mcwriter.utils import (serialize_dotted_path_dict,
                            serialize_lists_input,
                            serialize_members_input,
                            serialize_tags_input,
                            prepare_batch_data_lists,
                            prepare_batch_data_add_members,
                            prepare_batch_data_delete_members,
                            _setup_client,
                            _verify_credentials,
                            batch_still_pending,
                            wait_for_batch_to_finish,
                            write_batches_to_csv)
from mcwriter.exceptions import ConfigError, MissingFieldError

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

def test_serializing_nested_path():
    flat = {'name': 'Robin',
            'contact__address': 'Foobar',
            'contact__country': 'Czechia',
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

def test_preparing_batch_data_for_delete():
    serialized_data = [{'list_id': 'foo', 'subscriber_hash': 'abc', 'email_address': 'me@ex.co'}]
    expected = {
        'operations': [
            {'method': 'DELETE',
             'path': '/lists/foo/members/abc',
             'operation_id': 'me@ex.co'}
        ]
    }
    prepared = prepare_batch_data_delete_members(serialized_data)
    assert prepared == expected

def test_serializing_members_input(new_members_csv):
    serialized = serialize_members_input(new_members_csv.name, action='add_or_update', chunk_size=1)
    first_chunk = next(serialized)
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
    assert first_chunk[0] == expected[0]
    second_chunk = next(serialized)
    assert second_chunk[0] == expected[1]
    with pytest.raises(StopIteration):
        next(serialized)

def test_serializing_members_input_linked_to_lists(new_members_csv_linked_to_lists,
                                                   created_lists):
    serialized = serialize_members_input(
        new_members_csv_linked_to_lists.name,
        action='add_or_update',
        created_lists=created_lists)
    first_chunk = next(serialized)
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
    assert first_chunk == expected


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
    with pytest.raises(MissingFieldError):
        client = _setup_client(params, enabled=False)


def test_veryifying_credentials_fails_on_wrong_apikey(client, monkeypatch):
    def raise_http_error():
        err = requests.HTTPError("WRONG!")
        class Resp:
            status_code = 401
        err.response = Resp()
        raise err

    monkeypatch.setattr(client.api_root, 'get', raise_http_error)
    with pytest.raises(ConfigError) as excinfo:
        _verify_credentials(client)
    excinfo.match('Invalid credentials')


def test_veryifying_credentials_wrong_apikey_ConnectionError(client, monkeypatch):
    def raise_ConnectionError():
        raise requests.ConnectionError("WRONG!")

    monkeypatch.setattr(client.api_root, 'get', raise_ConnectionError)
    with pytest.raises(ConfigError) as excinfo:
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


def test_parsing_tags_table(add_tags_csv):
    serialized = serialize_tags_input(add_tags_csv.strpath)
    expected = [{
        'list_id': 'abc0123',
        'name': 'My first tag',
        'type': 'text',
        'tag': "MYFIRST",
        'required': False,
        'options': {'size': 255}
    }]
    assert serialized == expected


def test_parsing_tags_table_with_custom_id(add_tags_csv_custom_id):
    created_lists = {'wizards': 'ab0123'}
    serialized = serialize_tags_input(add_tags_csv_custom_id.strpath, created_lists)
    expected = [{
        'list_id': 'ab0123',
        'name': 'My first tag',
        'type': 'text',
        'tag': "MYFIRST",
        'required': False,
        'options': {'size': 255}
    }]
    assert serialized == expected

def test_writing_batches_csv(tmpdir):
    outpath = tmpdir.join("out.csv")
    batches = [{'_links': [{'href': 'https://us16.api.mailchimp.com/3.0/batches',
                            'rel': 'delete'}],
                'completed_at': '2017-11-01T10:05:15+00:00',
                'errored_operations': 13,
                'finished_operations': 500,
                'id': '71efba6182',
                'response_body_url': 'https://mai',
                'status': 'finished',
                'submitted_at': '2017-11-01T10:00:49+00:00',
                'total_operations': 500},
               {'_links': [{'href': 'https://us16.api.mailchimp.com/3.0/batches',
                            'rel': 'delete'}],
                'completed_at': '2017-11-01T10:05:15+00:00',
                'errored_operations': 13,
                'finished_operations': 500,
                'id': '71efba6182',
                'response_body_url': 'https://mai',
                'status': 'finished',
                'submitted_at': '2017-11-01T10:00:49+00:00',
                'total_operations': 500}
    ]
    write_batches_to_csv(batches, outpath.strpath)

    with open(outpath.strpath, 'r') as f:
        assert len(f.readlines()) == 3
    with open(outpath.strpath, 'r') as f:
        reader = csv.DictReader(f)
        assert '_links' not in reader.fieldnames
        assert 'id' in reader.fieldnames
