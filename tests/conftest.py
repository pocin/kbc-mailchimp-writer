import pytest
from tempfile import NamedTemporaryFile
import mailchimp3


@pytest.fixture
def new_lists_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''name,contact.company,contact.address1,contact.address2,contact.city,contact.state,contact.zip,contact.country,contact.phone,permission_reminder,use_archive_bar,campaign_defaults.from_name,campaign_defaults.from_email,campaign_defaults.subject,campaign_defaults.language,notify_on_subscribe,notify_on_unsubscribe,email_type_option,visibility
Wizards of the world,Magical company ltd.,4 Privet Drive,,Wizardshire,Wonderland,66678,Wonderland,,"You are in this list, because you just turned 11 and have magical abilities",false,Albus Dumlbedore,dark_mage001@email.com,"Welcome, young wizard!",English,,,true,prv
Wizxxrds of the world,Mxxgicxxl compxxny ltd.,4 Privet Drive,,Wizxxrdshire,Wonderlxxnd,66678,Wonderlxxnd,,"You xxre in this list, becxxuse you just turned 11 xxnd hxxve mxxgicxxl xxbilities",false,XXlbus Dumlbedore,dxxrk_mxxge001@emxxil.com,"Welcome, young wizxxrd!",English,,,true,prv''')
    inputs.close()
    return inputs


@pytest.fixture
def update_lists_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''list_id,name,contact.company,contact.address1,contact.address2,contact.city,contact.state,contact.zip,contact.country,contact.phone,permission_reminder,use_archive_bar,campaign_defaults.from_name,campaign_defaults.from_email,campaign_defaults.subject,campaign_defaults.language,notify_on_subscribe,notify_on_unsubscribe,email_type_option,visibility
1234abc,Wizards of the world,Magical company ltd.,4 Privet Drive,,Wizardshire,Wonderland,66678,Wonderland,,"You are in this list, because you just turned 11 and have magical abilities",false,Albus Dumlbedore,dark_mage001@email.com,"Welcome, young wizard!",English,,,true,prv
1234xxbc,Wizxxrds of the world,Mxxgicxxl compxxny ltd.,4 Privet Drive,,Wizxxrdshire,Wonderlxxnd,66678,Wonderlxxnd,,"You xxre in this list, becxxuse you just turned 11 xxnd hxxve mxxgicxxl xxbilities",false,XXlbus Dumlbedore,dxxrk_mxxge001@emxxil.com,"Welcome, young wizxxrd!",English,,,true,prv''')
    inputs.close()
    return inputs

@pytest.fixture
def client():
    return mailchimp3.MailChimp('foo', 'bar', enabled=False)


@pytest.fixture
def new_members_csv():
    inputs = NamedTemporaryFile(delete=False)
    inputs.write(b'''email_address,vip,interests.1234abc,interests.abc1234,status,email_type_option,merge_fields.*|FNAME|*
robin@keboola.com,true,true,true,subscribed,true,Robin
foo@bar.com,false,true,false,pending,false,''')
    inputs.close()
    return inputs
