import pytest
from mcwriter.writer import create_lists, update_lists, add_members_to_lists
from tempfile import NamedTemporaryFile


def test_creating_lists_has_ok_syntax(new_lists_csv, client):
    create_lists(client, csv_lists=new_lists_csv.name, batch=False)
    assert True

def test_creating_lists_has_ok_syntax(new_lists_csv, client):
    create_lists(client, csv_lists=new_lists_csv.name, batch=True)
    assert True


def test_updating_lists_has_ok_syntax(update_lists_csv, client):
    update_lists(client, csv_lists=update_lists_csv.name)
    assert True

def test_adding_members_to_list_has_correct_syntax(new_members_csv, client):
    """Not sure what other things to test here..."""
    add_members_to_lists(client, new_members_csv.name, batch=False)
