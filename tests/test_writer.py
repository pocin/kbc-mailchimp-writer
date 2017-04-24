import pytest
from mcwriter.writer import (create_lists, update_lists,
                             add_members_to_lists, _create_lists_serial)
from tempfile import NamedTemporaryFile


def test_creating_lists_has_ok_syntax(new_lists_csv, client):
    create_lists(client, csv_lists=new_lists_csv.name)
    assert True

def test_updating_lists_has_ok_syntax(update_lists_csv, client):
    update_lists(client, csv_lists=update_lists_csv.name)
    assert True

def test_adding_members_to_list_without_custom_ids(new_members_csv, client):
    """Not sure what other things to test here..."""
    add_members_to_lists(client, new_members_csv.name, batch=False, created_lists=None)

def test_adding_members_to_list_with_custom_ids(new_members_csv, client):
    """Not sure what other things to test here..."""
    # returned by the create_lists function
    created_lists = {'custom_list1': 'mailchimphash'}
    add_members_to_lists(client, new_members_csv.name, batch=False,
                         created_lists=created_lists)

def test_adding_members_to_list_has_correct_syntax(new_members_csv, client):
    """Not sure what other things to test here..."""
    add_members_to_lists(client, new_members_csv.name, batch=False)

def test_creating_lists_returns_custom_ids(client, monkeypatch):
    serialized_data = [{
        'name': 'a mailing list',
        'custom_id': 'custom_list_1',
    },
    {
        'name': 'a second mailing list',
        'custom_id': 'custom_list_2'
    }]
    lists = _create_lists_serial(client, serialized_data)
    assert lists == {'custom_list_1': 'mailchimp_list_id',
                     'custom_list_2': 'mailchimp_list_id'}

