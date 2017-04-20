import mailchimp3
import pytest
from mcwriter.writer import create_lists
from tempfile import NamedTemporaryFile

@pytest.fixture
def new_list_input_csv():
    templists = NamedTemporaryFile(delete=False)
    templists.write(b'''"name","contact.company","contact.address1","contact.address2","contact.city","contact.state","contact.zip","contact.country","contact.phone","permission_reminder","use_archive_bar","campaign_defaults.from_name","campaign_defaults.from_email","campaign_defaults.subject","campaign_defaults.language","notify_on_subscribe","notify_on_unsubscribe","email_type_option","visibility"
"robin","COMPANYLTD","ADRESA123",,"OSTRAVA","CESKO",12356,"CEESKO",123456789,"YOU GAVE US YOUR MAIL",,"FROM ME","FROMME@mail.com","NEWSLETTER","CZENGLISH",,,"false","prv"''')
    templists.close()
    return templists

def test_creating_lists_has_ok_syntax(new_list_input_csv):
    client = mailchimp3.MailChimp('foo', 'bar', enabled=False)
    create_lists(client, csv_lists=new_list_input_csv.name, batch=False)
    assert True

def test_creating_lists_has_ok_syntax(new_list_input_csv):
    client = mailchimp3.MailChimp('foo', 'bar', enabled=False)
    create_lists(client, csv_lists=new_list_input_csv.name, batch=True)
    assert True
