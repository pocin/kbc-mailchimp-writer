import pytest
import json
from tempfile import NamedTemporaryFile
from mcwriter.utils import (serialize_dotted_path_dict,
                            serialize_lists_input,
                            serialize_members_input,
                            prepare_batch_data)


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
                 'visibility': 'prv'},
                ]


    assert expected[0] == serialized[0]
    assert expected[1] == serialized[1]


def test_preparing_batch_data():
    template = {
        'method': 'POST',
        'path': '/lists',
        'body': None}

    data = [{'foo':'bar', 'baz':'qux'},
            {'foo':'bar2', 'baz': 'quxx'}]

    batch_data = prepare_batch_data(template, data)

    expected = {'operations': [
        {'method': 'POST',
         'path': '/lists',
         'body': json.dumps({'foo':'bar', 'baz':'qux'})},
        {'method': 'POST',
         'path': '/lists',
         'body': json.dumps({'foo':'bar2', 'baz': 'quxx'})}
    ]}
    assert batch_data == expected

def test_serializing_members_input(new_members_csv):
    serialized = serialize_members_input(new_members_csv.name)
    expected = [
        {'email_address': 'robin@keboola.com',
         'list_id': '12345',
         'vip': True,
         'interests' : {
             '1234abc': True,
             'abc1234': True},
         'status': 'subscribed',
         'email_type_option': True,
        'merge_fields': {'*|FNAME|*':'Robin'}
        },
        {'email_address': 'foo@bar.com',
         'list_id': '12345',
         'vip': False,
         'interests' : {
             '1234abc': True,
             'abc1234': False},
         'status': 'pending',
         'email_type_option': False,
         'merge_fields': {'*|FNAME|*': ''}
        }
    ]
    assert serialized == expected

