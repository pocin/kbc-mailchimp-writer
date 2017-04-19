# Tasks
# About
Mailchimp writer should be able to create and manage mailing lists. Managing includes updating and removing email addresses.

# Resources
Implement as an Keboola extension: https://developers.keboola.com/extend/docker/
API DOCS here v3 here: http://developer.mailchimp.com/documentation/mailchimp/guides/get-started-with-mailchimp-api-3/

https://github.com/charlesthk/python-mailchimp

# Configuration
The writer enables:

1. Creation of new mailing lists
2. Updating details of existing mailing lists
3. Adding and editing email addresses in mailing lists


## Creation of new mailing lists
[According to the mailchimp v3 API](http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists),
[or here](https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json)
these details can be used to create a mailing list:
```python
 "name",
 "contact.company",
 "contact.address1",
 "contact.address2",
 "contact.city",
 "contact.state",
 "contact.zip",
 "contact.country",
 "contact.phone",
 "permission_reminder",
 "use_archive_bar",
 "campaign_defaults.from_name",
 "campaign_defaults.from_email",
 "campaign_defaults.subject",
 "campaign_defaults.language",
 "notify_on_subscribe",
 "notify_on_unsubscribe",
 "email_type_option",
 "visibility"]
```
Each keyword should be a column name in the `new_lists.csv` input file ([see the template](./templates/new_lists.csv)). Each row represents a new mailing list.

