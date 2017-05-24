import pytest
import requests
from mcwriter.writer import (create_lists, update_lists,
                             create_tags, add_members_to_lists,
                             _create_lists_serial)
from tempfile import NamedTemporaryFile
from mcwriter.exceptions import CleaningError, MissingFieldError, UserError
import mcwriter


def test_creating_lists_has_ok_syntax(new_lists_csv, client):
    create_lists(client, csv_lists=new_lists_csv.name)
    assert True

def test_updating_lists_has_ok_syntax(update_lists_csv, client):
    update_lists(client, csv_lists=update_lists_csv.name)
    assert True

def test_adding_members_to_list_without_custom_ids(new_members_csv, client):
    """Not sure what other things to test here..."""
    add_members_to_lists(client, new_members_csv.name, batch=False, created_lists=None)

def test_adding_members_to_list_with_custom_ids(new_members_csv_linked_to_lists, client):
    """Not sure what other things to test here..."""
    # returned by the create_lists function
    created_lists = {'custom_list1': 'mailchimphash'}
    add_members_to_lists(client, new_members_csv_linked_to_lists.name, batch=False,
                         created_lists=created_lists)

def test_adding_members_to_list_has_correct_syntax(new_members_csv, client):
    """Not sure what other things to test here..."""
    add_members_to_lists(client, new_members_csv.name, batch=False)

def test_creating_lists_returns_custom_ids(client):
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


def test_creating_lists_returns_empty_dict_if_not_custom_ids(client):
    serialized_data = [{'name': 'a mailing list'},
                       {'name': 'a second mailing list'}]
    lists = _create_lists_serial(client, serialized_data)
    assert lists == {}


def test_running_app_catches_http_error_as_app_error(monkeypatch):
    def failing_setup(*args, **kwargs):
        # is an application error
        raise requests.HTTPError("Some requests error")

    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)
    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 2


def test_running_app_catches_generic_exception_as_app_eror(monkeypatch):
    def failing_setup(*args, **kwargs):
        raise Exception("Some app error")
    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)

    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 2


def test_running_app_catches_generic_exception_as_app_eror(monkeypatch):
    def failing_setup(*args, **kwargs):
        raise ValueError("Some app error")
    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)

    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 2

def test_running_app_catches_cleaning_error_as_user_error(monkeypatch):
    def failing_setup(*args, **kwargs):
        raise CleaningError("Some app error")
    # we patch the set_up function because its easier and we do not really care
    # where the exception happens as long as it is iwthin the run() func.

    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)

    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 1

def test_running_app_catches_cleaning_error_as_user_error(monkeypatch):
    def failing_setup(*args, **kwargs):
        raise MissingFieldError("Some app error")
    # we patch the set_up function because its easier and we do not really care
    # where the exception happens as long as it is iwthin the run() func.

    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)

    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 1


def test_running_app_catches_generic_UserError_as_user_error(monkeypatch):
    def failing_setup(*args, **kwargs):
        raise UserError("Some user error")
    # we patch the set_up function because its easier and we do not really care
    # where the exception happens as long as it is iwthin the run() func.

    monkeypatch.setattr('mcwriter.writer.set_up', failing_setup)

    with pytest.raises(SystemExit) as excinfo:
        mcwriter.writer.run()
    assert excinfo.value.code == 1

def test_creating_tags_has_ok_syntax(client, add_tags_csv):
    create_tags(client, csv_tags=add_tags_csv.strpath)
    assert 1


def test_creating_tags_with_created_lists_has_ok_syntax(client, add_tags_csv_custom_id):
    created_lists = {'wizards': 'abc0123'}
    create_tags(client, csv_tags=add_tags_csv_custom_id.strpath, created_lists=created_lists)
    assert 1
