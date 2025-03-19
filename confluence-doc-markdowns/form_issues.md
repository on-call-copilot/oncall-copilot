# Form issues

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
