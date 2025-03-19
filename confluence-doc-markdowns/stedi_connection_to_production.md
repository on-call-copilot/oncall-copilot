# [EDI] Ideon cut over and move in-house connection to production

```
Prerequisites
Instructions
Common errors
💬 Reach out to us
```

This tool serves 2 purposes :

```
Cut over communications to Ideon for a particular company and carrier.
Move the in house (Stedi) connection for the company and carrier to production so files can be sent automatically.
```

## Prerequisites

Before using this tool, make sure that you have followed these steps:

1. Onboarding the group - [EDI] Onboarding Groups Over Partner and Vendor
2. Triggered ingestion files for the group and carrier - In-House EDI (Stedi) Custom Trigger Retool

## Instructions

1. Input the company ID and click on submit. This will show you a list of connections. Each connection will have a carrier, list of lines and
   other details.
2. Pick the connection ID based on the carrier and lines that you want, and paste it in the Move connection to Stedi box.
3. Click on submit. This will move the connection to production and cut off the Ideon comms (if there are no errors).

```
You can find the tool here!
```

## Common errors

You might encounter some errors while moving the connection. Here are some of them and how to resolve them:

```
Error message : Vericred connection is not yet marked as inactive.
Resolution : This means that the vericred file feed has not yet been marked as inactive. Make sure you’ve expired the coverage periods
for the company and carrier on Ideon. If they’re expired on Ideon and you still see this error, please try again after a few hours as our
system takes some time to sync the data from Ideon.
Error message : No accepted snapshots found for company and carrier
Resolution : This means that no snapshots have been marked as accepted. Go to the file trigger tool (Prerequisite #2) and mark one of
the snapshots as accepted.
```

If you see any other errors, please reach out to the Benefits Marketplace Integrations team below.

## 💬 Reach out to us

Still have questions or facing some errors? Slack us on #team-benefits-marketplace-integrations
