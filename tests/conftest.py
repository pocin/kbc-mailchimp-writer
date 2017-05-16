import pytest
from tempfile import NamedTemporaryFile
import mailchimp3


@pytest.fixture
def new_lists_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''custom_id,name,contact__company,contact__address1,contact__address2,contact__city,contact__state,contact__zip,contact__country,contact__phone,permission_reminder,use_archive_bar,campaign_defaults__from_name,campaign_defaults__from_email,campaign_defaults__subject,campaign_defaults__language,notify_on_subscribe,notify_on_unsubscribe,email_type_option,visibility
custom_list1,Wizards of the world,Magical company ltd.,4 Privet Drive,,Wizardshire,Wonderland,66678,Wonderland,,"You are in this list, because you just turned 11 and have magical abilities",false,Albus Dumlbedore,dark_mage001@email.com,"Welcome, young wizard!",English,,,true,prv
custom_list2,Wizxxrds of the world,Mxxgicxxl compxxny ltd.,4 Privet Drive,,Wizxxrdshire,Wonderlxxnd,66678,Wonderlxxnd,,"You xxre in this list, becxxuse you just turned 11 xxnd hxxve mxxgicxxl xxbilities",false,XXlbus Dumlbedore,dxxrk_mxxge001@emxxil.com,"Welcome, young wizxxrd!",English,,,true,prv''')
    inputs.close()
    return inputs


@pytest.fixture
def update_lists_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''list_id,name,contact__company,contact__address1,contact__address2,contact__city,contact__state,contact__zip,contact__country,contact__phone,permission_reminder,use_archive_bar,campaign_defaults__from_name,campaign_defaults__from_email,campaign_defaults__subject,campaign_defaults__language,notify_on_subscribe,notify_on_unsubscribe,email_type_option,visibility
1234abc,Wizards of the world,Magical company ltd.,4 Privet Drive,,Wizardshire,Wonderland,66678,Wonderland,,"You are in this list, because you just turned 11 and have magical abilities",false,Albus Dumlbedore,dark_mage001@email.com,"Welcome, young wizard!",English,,,true,prv
1234xxbc,Wizxxrds of the world,Mxxgicxxl compxxny ltd.,4 Privet Drive,,Wizxxrdshire,Wonderlxxnd,66678,Wonderlxxnd,,"You xxre in this list, becxxuse you just turned 11 xxnd hxxve mxxgicxxl xxbilities",false,XXlbus Dumlbedore,dxxrk_mxxge001@emxxil.com,"Welcome, young wizxxrd!",English,,,true,prv''')
    inputs.close()
    return inputs

@pytest.fixture
def client(monkeypatch):
    def fake_response(data):
        return {'id': 'mailchimp_list_id'}
    client = mailchimp3.MailChimp('foo', 'bar', enabled=False)
    monkeypatch.setattr(client.lists, 'create', fake_response)
    return client


@pytest.fixture
def new_members_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''email_address,vip,interests__1234abc,interests__abc1234,status,email_type,merge_fields__*|FNAME|*,list_id,status_if_new
robin@keboola.com,true,true,true,subscribed,true,Robin,12345,subscribed
foo@bar.com,false,true,false,pending,false,,12345,subscribed''')
    inputs.close()
    return inputs

@pytest.fixture
def new_members_csv_linked_to_lists():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''email_address,vip,interests__1234abc,interests__abc1234,status,email_type,merge_fields__*|FNAME|*,list_id,status_if_new,custom_list_id
robin@keboola.com,true,true,true,subscribed,true,Robin,12345,subscribed,custom_list1
foo@bar.com,false,true,false,pending,false,,12345,subscribed,custom_list1''')
    inputs.close()
    return inputs

@pytest.fixture
def created_lists():
    return {'custom_list1': 'mailchimp_list_id'}
