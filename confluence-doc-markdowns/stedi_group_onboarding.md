# [EDI] Onboarding Groups Over Partner and Vendor

Table of Contents :
Overview
Instructions
Description of fields
📤 Onboarding companies and uploading CSV
FAQs
Next steps
💬 Reach out to us

## Overview

This guide describes how to use the superuser tool to onboard companies for a partner and vendor as part of our in-house EDI. You can
enter the details of each company one by one or even bulk onboard a list of companies by uploading a CSV. The overall process looks like
this :
Enter the data of companies to be onboarded (by either of the above mentioned ways)
Click on onboard, after which the tool will show a pop-up displaying a list of companies onboarded successfully and another list of
companies which could not be onboarded due to some errors.
Go back and resolve these errors and click on onboard again!

## Instructions

### Description of fields

Here’s a description of the fields you will need to enter for each company :

```
Note : This tool in used as a part of the process of onboarding groups from Ideon to inhouse EDI. Only Stedi is the supported
vendor for now. Do not use this for any other vendors.
```

```
You can find the tool here!
```

```
Company ID Company ID of the company to be
onboarded
```

```
A valid Rippling company ID string.
```

```
Partner/Carrier ID ID of the partner/carrier A valid carrier ID. Refer this page for getting the carrier ID.
Vendor Select the vendor (Single select) If entering manually : Select from the available list of vendors.
If uploading a CSV : Look at the available list of vendors in the
dropdown and enter one of the vendor names in your CSV
column.
Benefits List of benefits for this particular
configuration of company, partner and
vendor. (Multi select)
```

```
If entering manually : Select from the available list of benefits.
If uploading a CSV : Look at the available list of benefits in the
dropdown and enter a list of comma separated benefits in your
```

```
Field Description Accepted values
```

```
Only Stedi is allowed as a vendor
for now.
```

###  How to get mapping ID?

###  How to get partnership andtransaction setting ID?

### 📤 Onboarding companies and uploading CSV

1. Open the superuser tool and click on “ _Import CSV”._ Then click on “ _download template”_ to download a template CSV file which will have
   the column headers.
2. Fill the CSV file. Each row corresponds to a company so you can add multiple rows to bulk onboard companies. Make sure to look at
   the above section before this step.

```
CSV column.
Example : For multiple - Medical, Dental
For single - Vision
Convention EDI EDI convention value. This is provided by
the carrier and is usually present in the
carrier guide.
```

```
Convention EDI = “005010X220A1“
```

```
Partner platform For all groups on the UHC Prime platform,
please add the name of the platform.
```

```
Partner platform = Prime
*This field is ONLY for UHC Prime groups and is case
sensitive”
Mapping ID ID of the mapping for partner and vendor.
(Check below screenshots for more
details)
```

```
Any string value is accepted.
Example - Mapping ID of Cigna on Stedi.
Cigna FACETS Mapping ID:
01HSD4R7N9YH4J85HJ4VFWWNJS
Cigna ACE Mapping ID: 01HZP1KW6MJN6FDMYDSPAV206W
UHC PRIME Mapping ID: 01J1F01QF5K60TST268A8C4XH
UHC USP Mapping ID: 01J1A3X7C1G4A5H8K0F0CQ82N
Partnership ID Partnership ID for company-partner-vendor
(Check below screenshots for more
details)
```

```
Any string value is accepted.
```

```
File prefix Prefix to be applied on files. This is
provided by the carrier (Check the file
generation tracker sheet for this carrier link
here)
```

```
Any string value is accepted.
Example : If the file name that the carrier expects is
NCZ1000__ncz0001i.119624.*.txt , then the file prefix value
is NCZ1000__ncz0001i.
Transaction setting ID Transaction setting ID (Check below
screenshots for more details)
```

```
005010X220A1-834-prod
```

```
Transmission
Frequency
```

```
Frequency of transmission. If entering manually : Select from the available list of
frequencies.
If uploading a CSV : Look at the available list of frequencies in
the dropdown and enter one of the frequencies in your CSV
column.
```

```
Currently, we have set this value to
be Tuesday in code. It will be
configurable in future.
```

3. Upload the CSV file on the tool and map the columns headers and values.
4. Click on “ _Onboard these groups”._ The tool will then display a pop-up displaying a list of companies onboarded successfully and another
   list of companies which could not be onboarded due to some errors. Go back and resolve these errors, and try again for the erroneous
   companies and you’re done!

## FAQs

```
How will the system handle the duplicates? what if we try to onboard a client that we have already onboarded in the past?
The system will not create any duplicates as long as a combination of group, carrier and benefits is unique. It will edit the
information of the group if it is already present.
For example -
Group - PlayVox, Carrier - Cigna , Benefits - Medical -> Assume this combination already exists in the system.
Then for the same values of group, carrier and benefits, no new entry will be created if you edit the remaining fields like file prefix or
transaction setting ID etc.
However, if you create a new entry as following :
Group - PlayVox, Carrier - Cigna , Benefits - Dental-> Then we will create a new entry for this combination. The idea
here is that benefits that are clubbed together in one single entry will be sent in the same file.
Is there a way to edit a group’s information? for example the file name.
To update the details of an existing group in the system, you can simply re-enter the group's information in the tool. This process will
override the previous values with the new ones you provide. It's important to note that as long as the combination of Company,
Carrier, Benefits, and Vendor remains the same, you can freely modify the other fields associated with the group. These fields
might include details such as the file name, file prefix, or transaction setting ID.
For example, if you need to change the file name or update any other specific settings, you can do so by entering the group's
existing combination of Company, Carrier, Benefits, and Vendor. The system will recognize this combination and apply your
changes to the corresponding fields without creating a duplicate entry.
This functionality ensures that you have the flexibility to update and maintain accurate information for each group while preserving
the integrity of the unique combinations of Company, Carrier, Benefits, and Vendor.
When to re-onboard vs when to edit?
If you need to change any of the core components—such as the Carrier, Benefits, or Vendor—associated with a company, a re-
onboarding process is necessary. This is because changing these elements alters the unique combination that identifies the
configuration in the system.
Re-onboarding ensures that the system accurately reflects the new setup and appropriately handles the data and interactions with
carriers and vendors.
For any other fields such as mapping ID, transaction setting ID, file prefix, transmission frequency etc., an edit will suffice.
Note that you cannot make any changes to the comfiguration once a connection is in production. You will have to do a re-
onboarding.
```

## Next steps

You have completed the first step in the process of onboarding groups on a partner and vendor. For the successfully onboarded groups in
this step, the next steps are as follows.
Head over to this retool to trigger ingestion files for the company.
Retool link
Documentation for the retool : In-House EDI (Stedi) Custom Trigger Retool

```
After the carrier accepts the ingestion file for the group, raise a ticket for engineering to migrate the group from Ideon to the
vendor(Stedi in this case).
Slack thread
Example ticket : BENINTEG-1433: Migrate 7 more groups to production for weekly transmission file DONE
```

## 💬 Reach out to us

Still have questions or facing some errors? Slack us on #team-benefits-marketplace-integrations
