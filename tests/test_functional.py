import pytest
import time
from mcwriter.writer import update_members, delete_members
from mailchimp3 import MailChimp
import requests
import os
from hashlib import md5

TEST_LIST_ID = os.getenv("MC_TEST_LIST_ID")
TEST_EMAIL = 'robin@keboola.com'
TEST_EMAIL_HASH = md5(TEST_EMAIL.encode('utf-8')).hexdigest()

@pytest.yield_fixture
def client():
    yield MailChimp('', os.getenv("MC_TEST_APIKEY"))



def test_updating_members_batch(client, tmpdir):
    now = str(time.time())
    csv = tmpdir.join('update_members.csv')
    csv.write("""list_id,email_address,merge_fields__UPD_BATCH
{list_id},{email},{upd_value}""".format(
        list_id=TEST_LIST_ID,
        email=TEST_EMAIL,
        upd_value=now))
    update_members(client, csv.strpath, batch=True)

    updated = client.lists.members.get(list_id=TEST_LIST_ID, subscriber_hash=TEST_EMAIL_HASH)
    current_value = updated['merge_fields']['UPD_BATCH']

    assert current_value == now

def test_updating_members_serial(client, tmpdir):
    now = str(time.time())
    csv = tmpdir.join('update_members.csv')
    csv.write("""list_id,email_address,merge_fields__UPD_SER
{list_id},{email},{upd_value}""".format(
    list_id=os.getenv("MC_TEST_LIST_ID"),
    email=TEST_EMAIL,
    upd_value=now))
    update_members(client, csv.strpath, batch=False)

    updated = client.lists.members.get(list_id=TEST_LIST_ID, subscriber_hash=TEST_EMAIL_HASH)
    current_value = updated['merge_fields']['UPD_SER']

    assert current_value == now


def test_deleting_member(client, tmpdir):
    now = str(time.time())
    test_mail = b'robcin@seznam.cz'
    test_mail_str = test_mail.decode('utf-8')
    test_hash = md5(test_mail).hexdigest()
    client.lists.members.create_or_update(
        list_id=TEST_LIST_ID,
        subscriber_hash=test_hash,
        data={'status': 'unsubscribed',
              'status_if_new': 'unsubscribed',
              'email_address': test_mail_str,
              'merge_fields': {
                  'UPD_SER': now
              }
        }
    )
    csv = tmpdir.join('delete_members.csv')
    csv.write("""list_id,email_address
{list_id},{email}""".format(
    list_id=os.getenv("MC_TEST_LIST_ID"),
    email=test_mail_str))
    delete_members(client, csv.strpath)

    with pytest.raises(requests.HTTPError) as excinfo:
        updated = client.lists.members.get(list_id=TEST_LIST_ID, subscriber_hash=test_hash)
    assert excinfo.value.response.status_code == 404
    assert "Resource Not Found" in excinfo.value.response.text
