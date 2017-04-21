import pytest
from mcwriter.writer import create_lists, update_lists
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
