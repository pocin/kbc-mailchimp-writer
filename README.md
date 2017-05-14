# About
![Mailchimp logo](media/mc_logo_64.png)

Keboola connection mailchimp writer

# Resources
Implement as
an [Keboola extension](https://developers.keboola.com/extend/docker/) Check out
complete
[Mailchimp API v3 docs](http://developer.mailchimp.com/documentation/mailchimp/guides/get-started-with-mailchimp-api-3/)
if you are unsure about some fields:

# Configuration
Only your Mailchimp api encrypted key ([Obtain here](https://admin.mailchimp.com/account/api/)) is required 
```javascript
{
    #apikey: "===KEBOOLA-ENCRYPTED-APIKEY-FOOBAR12345"
}

```

The writer enables:
1. Creation of new mailing lists

2. Updating details of existing mailing lists

3. Adding and editing email addresses in mailing lists

**The tables you provide determine the writer's behavior**. See below for the
actual table structures, [See here for actual examples](templates). 
For the sake of clarity, the **input tablenames are hardcoded** and you can't change that.

| Supplied tables                    | Action                                                                                                           |
| ----------------                   | --------                                                                                                         |
| `update_lists.csv`                 | Update existing lists.                                                                                           |
| `new_lists.csv`                    | Add lists                                                                                                        |
| `add_members.csv`                  | Add members to existing lists                                                                                    |
| `new_lists.csv`, `add_members.csv` | Create lists defined in the `new_lists.csv`, then use the `custom_list_id` to add members to newly created lists |


- Fields marked with `*` (below) are mandatory
- You can completely left out the non-mandatory columns from the csv.
- Boolean values must be either `true` or `false` (empty string is treated as `false`).

## Creation of new mailing lists
[According to the mailchimp v3 API](http://developer.mailchimp.com/documentation/mailchimp/reference/lists/#create-post_lists),
[or here](https://us1.api.mailchimp.com/schema/3.0/Definitions/Lists/POST.json)
these columns can be used to create a mailing list:

```
"custom_id", # string, optional; If you want to create list and fill them with
             # contacts in one go, suppliy this column. The value is any unique
             # custom identifier that links the list with the addresses in the 
             # table for adding members.
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

Each keyword should be a column name in the `new_lists.csv` input file
([see the template](./templates/new_lists.csv)). Each row represents a new
mailing list.

## Updating of existing mailing lists
Same columns as in `new_lists.csv`, however you should name the table `updated_lists.csv` in the input mapping.

## Adding members to lists

[The Mailchimp API](http://developer.mailchimp.com/documentation/mailchimp/reference/lists/members/#edit-put_lists_list_id_members_subscriber_hash) describes
what fields and their values can be used to add-or-update members to lists. Here
are the most important ones. Again, starred `*` fields are required, nested
values are separated with dot. The input table has to be named `add_members.csv` (define in the input mapping).

Members which are already in given list will be updated (only supplied values.
For exapmle the record's `vip` status will be left intact if it is already
present and the `vip` column is not defined in the input table.

### Columns
```
    "custom_list_id" #string, optional; if using the custom_id in the table for
                     # creating lists, use this to reference (as a one to many relationship)
                     # the lists you want the contact to be part of
    "list_id", #*string; the list where you want this member to be added
    "status_if_new", #*string; one of ["subscribed", "unsubscribed", "cleaned", "pending", "transactional"]
                     # Defineds which status will be assigned to existing email addressess
    "email_address", #*string
    "status", #*string one of ["subscribed", "unsubscribed", "cleaned", "pending", "transactional"]
    "interests.{interest_id}", #boolean
    "merge_fields.{merge_tag}", #str (see merge tags mailchimp cheatsheet)
    "language", #string
    "vip", #boolean
```

### Adding members to newly created lists
Use column `custom_list_id` in the `add_members.csv` input table, which references the column
`custom_list_id` in the `new_lists.csv` In this case, do not use the column `list_id`
in neither the `add_members.csv` nor in the `new_lists.csv`

### Adding members to already existing lists
Use column `list_id` in the `add_members.csv` input table to specify the list (found in the mailchimp website).

