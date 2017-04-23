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
these columns can be used to create a mailing list:
```python
 "name", #*string
 "contact.company", #*string
 "contact.address1", #*string
 "contact.address2", #string
 "contact.city", #*string
 "contact.state", #*string
 "contact.zip", #*string
 "contact.country", #*string
 "contact.phone", #string
 "permission_reminder", #*string
 "use_archive_bar", #true/false
 "campaign_defaults.from_name", #*string
 "campaign_defaults.from_email", #*string
 "campaign_defaults.subject", #*string
 "campaign_defaults.language", #*string
 "notify_on_subscribe", #string
 "notify_on_unsubscribe", #string
 "email_type_option", #*true/false
 "visibility" #pub/prv
```
Each keyword should be a column name in the `new_lists.csv` input file ([see the template](./templates/new_lists.csv)). Each row represents a new mailing list.

Fields marked with `*` are required. Strings can be empty `''`. Boolean values must be either `true` or `false` (empty string is treaded as `false`). You can completely left out the non-mandatory columns from the csv.

## Updating of existing mailing lists

## Adding members to existing lists
[The Mailchimp API] describes what fields and their values can be used to add members to lists. Here are the most important ones. Again, starred `*` fields are required, nested values are separated with dot.

```python
  "email_address": #*string
    "status", #*string one of ["subscribed", "unsubscribed", "cleaned", "pending", "transactional"]
    "interests.{interest_id}", #boolean
    "language", #string
    "vip", #boolean

```
