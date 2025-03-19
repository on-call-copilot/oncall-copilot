# Noyo Integration

Changes in our system need to be reflected in carriers eventually. There are multiple approaches, email/fax, EDI, and API. Historically,
email/fax dominated the sheer transaction volume. However, EDI/API are gaining increasing tractions as high automation/low operations
become important for scaling the business. Noyo is a vendor that provides API integration with some popular carriers.

Before any transactions can go through [occur during performAction of a **PendingAction** object, triggered during **autoSendForms** in
production], there are some setups need to be done. Most of the times, the setups are completely automated. However, there are still
cases where we are not able to/confident enough to automate, thus to be further improved.

# Supported Carriers

Beam, Guardian, Principal, and Unum.

# Transaction prerequisites & payload generation

## Group Connection

Currently, Noyo does not provide an API for submitting a group to carrier.

When a company is enrolling with a carrier for the very first time:

1. For BOR, we submit groups to carrier. In this case, we know exactly when submissions happen.
2. For BOB, currently, we don’t know when brokers submit groups. However, this is going to change soon.

When a company is already enrolled with a carrier, and is just transfering to Rippling, we should be able to find an existing connection in
Noyo.

Either case, once a carrier has the group installed [confirmation from carrier], we can expect to be able to find that company in Noyo
sometime later [Noyo periodically syncs with carriers on groups]. At this point, if there is no existing connection, then we need to request it.
There is one task for requesting Noyo group connections, and another one for syncing the connection status of requests.

Once a group is connected with a carrier, a group id will be assigned [the id of the group in Noyo, not to be confused with carrier group id.],
we should be able to send transactions of this group to the carrier through Noyo API [Given there are some plans, more to go for newly
added lines]. A group can potentially have different group ids for different carrier / carrier_group_id. And we save the information in
**NoyoCompanyCarrier** objects.


Group connection

# Sign in to your Google Account

```
You must sign in to access this content
```
```
Sign in
```

## Plan Mapping

Noyo represents plans differently from Rippling. Therefore, a transaction of a Rippling plan need to be converted to a transaction of a noyo
plan. [TODO: Adding new line for the first time] The mappings are modeled as **NoyoCompanyPlanInfo** objects.

Here are some of the most notable differences:

1. A plan in Rippling is based on **RelationshipChoices** , i.e. SELF, SPOUSE, DOMESTIC_PARTNER. In contrast, a plan in Noyo is
    based on eligible_member_types, and has finer granularity, e.g. ‘all’, ‘employee’, ‘child', ‘foster-child’, etc. The conversion from Rippling
    to Noyo is basically a one-to-many mapping, except for ‘ **all** ’ in Noyo, which requires special handling. [Rarely, we have many to many
    mappings.]
2. Typically, a Rippling plan can be converted to a Noyo plan, given the relationship type of the member [ _allowedRelationshipTypes_ in
    Rippling plan has to honored still]. However, there are exceptions. Noyo sometimes further splits 1 plan in carrier to multiple plans of
    theirs to express carrier classification based eligibility. e.g. For the same carrier plan, for ‘spouse’, there is one plan eligible for member
    group 123, and another plan eligible for emember group 456 and 789. In this case, we have to use carrier classification information
    [ **CarrierClassification** in Rippling model, /carrier_configurations in Noyo API] to uniquely convert a Rippling plan to a Noyo plan.
3. Each plan is of a line type. That is true for both Rippling and Noyo plans. However, some major distinctions exist for life & ADD plans.
    a. In Rippling, life & ADD plans are always bound as one plan. In contrast, Noyo have separate plans for life and ADD.
    b. Rippling distinguishes basic and voluntary life at line type level. However, both basic and voluntary life plans have the same line
       type in Noyo, and the plan_type field is used to distinguish them.
    c. For convenience, we map Rippling life & ADD plan to both life and ADD plans in Noyo. One problem for binding life & ADD together
       is that allowed relationships can be different for life and ADD plans. Therefore, we introduced a field
       **allowed_relationships_for_add** in Rippling life & ADD plan, which is used to determine if a ADD plan change should be included
       in addition to life plan change when converting a transaction of a life & ADD plan in Rippling to a Noyo transaction.


Plan Mapping

# Sign in to your Google Account

```
You must sign in to access this content
```
```
Sign in
```

## Member mapping

Member mapping is easier than plan mapping to some extent, as this is a one-to-one mapping. Plus, members associated with the same
subscriber can be mapped together. A Rippling member can be mapped to different Noyo person, given a group Noyo ID. For example,
one important use case is for handling PEO transition (either to/from), in which the the member stays the same, but a **NoyoMember** object
is created for the group Noyo ID the company moves to. Also, it is possible for different members of the same person i.e. for different roles,
to be mapped to the same Noyo person. One example is rehire, where there is at least one member object for the terminated role and
another one for the active role. Both member objects are mapped to the same Noyo ID.

# Operation Tools

## Company debugger

Here, we can see an overview of live group connections/assigned group ids. We can also request group connections by
carrier/carrier_group_id. For requested group connections, there is also information like status e.g. “noyo review” and relevant dates
information.

## Plan mapper

A link to plan mapper can be found in the company debugger page. There are four sections.

1. Map unmapped plans to Noyo plans. Most plan mapping issues should be able to be fixed here.
2. Add mappings to already mapped plans. In case there were mistakes in existing mappings, e.g. a life & ADD plan is only mapped to life
    plans in Noyo, a plan is only mapped to employee plans in Noyo, here is the place to make amendment.
3. View/Delete existing mappings.
4. Assign classification values to Noyo plans. As mentioned, when Noyo create multiple plans based on classification values, it is not
    sufficient to simply map a Rippling plan to all those Noyo plans. Here, one can associate a classification value to multiple Noyo plans.
    e.g. member group 123 is associated with dental plan 1 and vision plan C. Then, during a transaction, a member belongs to billing
    group abc, and member group 123 is eligible for that plan mapping, whereas a member belongs to billing group abc, and member
    group 456 is not.


# Task System

For the scenarios where we cannot automate, we create tasks that are actionable by the Ops team. There are two types of tasks, one for
setup, one for error detection.


## Setup Task

Setup tasks are categorized based on what prerequisites are missing. There are 4 types, “ **GROUP_CONNECTION** ", " **PLAN_MAPPING** ",
" **CARRIER_CONFIGURATION** ", and " **CONFIGURATION_ASSIGNMENT** ” [NOYO_PREREQUISITE_TYPES]. And there are two levels of
granularity, one is **BaseNoyoSetupTask,** and the other is **NoyoSetupTask**. Base tasks are at (company, carrier) level, and are what
being exposed directly. Each is the parent task of a group of setup tasks, which are used to track individual missing prerequisite. The tasks
are created daily by the job **check_for_noyo_transaction_prerequisites**.

1. A GROUP_CONNECTION task is created when a NoyoCompanyCarrier object does not have a noyo group id and a group connection
    has not been requested on it behalf. These can be handled in company debugger.
2. A PLAN_MAPPING task is created when a Rippling plan is not mapped to any Noyo plan [Thus there could be true negatives, e.g.
    when a someone only mapped a plan to Noyo plans for employee, but not to plans for dependents]. These can be handled in the plan
    mapper. NOTE: When a new line is added for the first time, it is possible that we don’t see any available Noyo plans for mapping
    because the carrier has not finished installation or Noyo isn’t synced up with the carrier yet. In such cases, we should check
    **ConfirmCompanyEnrollmentTask** first before we reach out to Noyo.
3. A CARRIER_CONFIGURATION task is created when there are classification values from Noyo API [/carrier_configurations] that we
    cannot find in our system [CarrierClassification]. These can handled by spoofing at the company, and adding missing values in
    insurance settings.
4. A CONFIGURATION_ASSIGNMENT task is created when the assignment of classification values to Noyo plans is invalid. There are
    two common cases:
       a. A Rippling plan is mapped to multiple Noyo plans with the same (line, eligible member types), but the mappings don’t have any
          assigned classification values to distinguish them.
       b. A Rippling plan is mapped to multiple Noyo plans with the same (line, eligible member types), but there are conflicts in the
          assignment, e.g. the same classification value exists at more than one mappings.

## Error Task [TODO]

```
A setup task for plan mapping
```

# Automation

## Group Connection

There are two jobs that run daily, one for requesting group connections [ **initiate_group_setups_for_noyo** ], and one for syncing existing
connection requests [ **sync_group_connections** ]. The first one is for BOR groups that are **eligible** for using Noyo for carrier
communications [NOTE: **Eligible** for Noyo means the carrier supports Noyo integration, that is different from **using** Noyo, e.g. BOB
groups can opt in/out Noyo integration]. When we request group connections, corresponding setup tasks are also created. They will be
auto-resolved when requests are complete. So why even bother creating those tasks in first place? Sometimes errors can occur for
connection requests, and we/Ops team may need to step in to handle those cases. Therefore, always creating setup tasks make it easier
for tracking such cases.

## Plan Matching

We call the process of automatically mapping our plans to Noyo plans “plan matching”. This is done daily in **matchPlansWithPlanInfos**.
Right now we only automatically map a plan to Noyo plans when we are 100 percent sure [i.e. we don’t depend on attributes like name,
etc.]. As a result, we currently cannot distinguish Rippling plans [ **CompanyPlanInfo** ] of the same line type. Therefore, we only do plan
matching when there is only one plan under the current line type. The job also auto resolves PLAN_MAPPING tasks if possible. It is worth
to mention that sometimes Noyo may delete/merge plans, causing some plan mappings becoming invalid. When that happens, we archive
such mappings along with relevant CONFIGURATION_ASSIGNMENT tasks.

## Member matching

We have a daily job that matches members in Rippling with members in Noyo. Subscribers can typically be matched with SSN. However,
SSN are often not available for dependents. Whenever SSN is not available, we do a fuzzy matching on DOB and name. Right now, we
use a very simple algorithm for it i.e. many noises, which is to be improved e.g. using some open source library instead.

# Internal Audits

There are two kinds of internal audits, one that sends debugging email to CARRIER_CONNECTIONS_ENG_TEAM_EMAIL_DICT, the
other that resides in super_user’s insurance audit dashboard. We use internal audits for things requiring engineering team’s involvement
[Either because the thing is still in development stage, thus unstable and volume is high, or because the nature of the problem cannot be
handled by Ops team solely. Eventually, we want those audits to be deprecated entirely/migrated to the task system.

Two of the most important audits are check_noyo_enrollment_mismatches/check_noyo_enrollment_mismatches_peo. They are all
based on check_enrollment_mismatches_for_nccs. Their predecessors are
checkForNoyoEnrollmentMismatches/check_for_noyo_enrollemnt_mismatches_peo/check_for_noyo_effective_date_mismatches
/check_for_noyo_effective_date_mismatches_peo. The two audits categorize enrollment mismatches by types. Mismatches are
grouped by role. The audits check both active/terminated roles. For the same person, only its most recent role is checked upon. Checks
won’t run on roles with in-process pending actions / companies with outstanding setup tasks.

# PEO

Noyo supports PEO plans for Guardian. There are two common scenarios, 1. the company already uses Noyo before moving to PEO. 2.
the company is on PEO directly. We currently don’t have a good support for the transition involved in the first case [Due to current member
mapping logic]. PEO plans are static [possibly updated once a year], and there is no new group connection involved. Thus we don’t
request group connection [i.e. already connected], do plan matching, or create setup tasks for PEO groups. Instead, PEO groups are
ingested daily in separate jobs directly i.e. creating NoyoCompanyCarrier, NoyoCompanyPlanInfo objects [ref.
**ingestPeoGroupToVendors** ].


# Resources

https://dashboard.noyoconnect.com/login

```
Noyo Group Benefits API
```
Internal
Noyo Connection Dashboard


