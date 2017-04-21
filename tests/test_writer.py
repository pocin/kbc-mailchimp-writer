import mailchimp3
import pytest
from mcwriter.writer import create_lists
from tempfile import NamedTemporaryFile
from conftest import new_lists_csv

def test_creating_lists_has_ok_syntax(new_lists_csv):
    client = mailchimp3.MailChimp('foo', 'bar', enabled=False)
    create_lists(client, csv_lists=new_lists_csv.name, batch=False)
    assert True

def test_creating_lists_has_ok_syntax(new_lists_csv):
    client = mailchimp3.MailChimp('foo', 'bar', enabled=False)
    create_lists(client, csv_lists=new_lists_csv.name, batch=True)
    assert True
