# Form issues

Rippling form ops team maps our insurance PDF form fields. The form ops team posts the mapped forms on Box and we copy over newly posted/updated forms from Box to our S3 bucket. Unfortunately, these forms uploaded by form ops may have issues. As a result, incorrect insurance forms slip into our system and cause many issues. For example, one form issue caused customers to be charged incorrectly. This was not discovered for months and resulted in monetary loss for our business. In another case, dependents were left insured, which caused bad customer experience and damaged Rippling's reputation. 


To address this issue, we built the form approval tool, which detects the form updates from Box, fill out the form with mock user data and presents each form on the dashboard as a review request for stakeholders to review. 

Also ensure that form files in box are named correctly for the event type and the information they are supposed to transmit to the carrier.

The reviewers are expected to review the forms on the dashboard, approve the correct forms, reject incorrect forms and report forms issues/request changes to the relevant stakeholders(insurance eng team, etc) as needed.

## When to file a Jira for a form issue?

```
A field is present but the information listed is incorrect
First check Form Field Details to confirm the information listed there is not correct
```

## When to make an Ops request for a form issue?

```
The form does not have a field or checkbox present on the PDF
this implies that data cannot be pulled onto the form as there is no field on the pdf to put the information from Rippling. This is an
issue with how the form is mapped.
If a new version of the form is needed
this implies that if we have an outdated form, the carrier will not process the enrollment or change. We actively look to update forms
to the most recent version but due to the sheer volume of carriers and supported transactions, there might be times when a specific
carrier form update is missed.
When an additional form is needed to process a request
in some cases , carriers may require more forms than listed in our product
If the form fields in the debugger are correct and it is not displaying that on the form it is a bug that requires an Ops request
```

```
Note:
*If the form field details in EE debugger are correct but the form is displaying incorrectly, that requires an Ops request. If the form
field details in EE debugger are incorrect, that would require a JIRA for Eng.
```

```
SUMMARY: If the issue revolves around missing fields, old forms, or missing forms it will require an Ops request.
```

