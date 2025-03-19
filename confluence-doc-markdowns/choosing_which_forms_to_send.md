# Choosing which forms to send

Before pending actions are sent to the carrier, we must first determine if the actions should be performed. This is calculated in the
shouldPerformAction function. The following goes over reasons why forms might not be sent, and why they are triggered.

## Disabled Actions

The simplest way for an action to not be send is if the disableAction flag is sent. This can be set manually for problematic actions that
we do not want to try to send. The other way this can be set is if the action is no longer relevant. Once the coverage lines associated with
an action are all expired, they will be automatically disabled so we don't consider them in the future.

## Unsubmittable Forms

Some actions are never submitted to carriers. These include actions that do not generate forms, such as offline changes, and actions with
only waiver forms. We also do not send forms if a company is no longer active on Rippling. Finally, if an event is archived by an insurance
admin, it also will not be sent.

## Rippling Not Managing Forms

Rippling only sends forms when we are managing forms for the company. However, once we are managing forms, we will not send the
entire backlog of actions for a company. Forms will only be sent after a date specified when form sending is turned on

## caveat: PEO forms

Forms for the Rippling PEO will always be sent, regardless of the company’s current form sending status. We do this for a simple reason:
if a company leaves the PEO, we still need to be able to send cancellation forms after we are no longer managing their forms.

## Not Ready To Perform The Action

Some actions are held back from being sent until some other criteria is met. For example, Open Enrollment events will only be sent after
the enrollment period is closed, rather than immediately after a subscriber make their enrollments. A company may also have custom
settings for when actions like a new hire enrollment or qualifying life event is sent.
