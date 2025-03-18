# Vericred Integration

# Models

## VericredComapnyCarrier

Represents a group on Vericred. We create a group for each pairing of company and carrier. A group corresponds to all of a company’s
employees, and coverage periods. The group’s id is stored in Rippling on the VericredCompanyCarrier’s vericredId field.

## VericredCompanyCoveragePeriodInfo

Think of coverage period as ccli group (list of cclis). A coverage period represents a single enrollment period for a group. Plans for a group
on the same carrier are on the same coverage period if the effective dates and insurance group id are the same.

The coverage period’s id is stored in Rippling on VericredCompanyCoveragePeriodInfo’s vericredId field.

4 states of coverage period

Vericred docs: Coverage Periods | Ideon - Enrollment

Frontend Dashboard - https://app.rippling.com/super_user/insurance/vericred-dashboard

## Coverage period creation

There are two entry points for creation of coverage period:

1. During initial ingestion
   a. When group is being put through EDI for very 1st time.
2. During renewal
   a. This is done automatically when the first action is performed using the new CompanyCarrierLineInfo. Our code first checks if a
   coverage period id exists on a CCLI. If it does not, then we will create a new one, and use that going forward.

## Coverage period update

We also periodically sync coverage period data from vericred via eta update_vericred_company_coverage_period_info

## VericredWorkLocationMap

Represents a work location in Vericred. This model creates a one to one relationship between a WorkLocation model in Rippling and a
work location id from Vericred. Vericred expects a work location for every domestic location of a company, and notes if they are physical or
remote.

## VericredCarrierIdMap

This is the current way we map subscribers to their Vericred ids. A subscriber has a different id for each carrier group in Vericred.
Currently, we store this in Rippling by creating a list of VericredCarrierIdMaps on a Member model. Each of these models maps a
carrier to an id for the Member. We are in the process of deprecating this model and replacing it with VericredMember, as described
below.

```
1 1) initial -> initiate connection with carrier.
2 2) test -> reconciliation phase where we weed out enrollment discrepancy between Rippling vs Carrier.
3 3) production -> successful live carrier sync established with no enrollment discrepancies.
4 4) expired -> expire carrier sync.
```

## VericredMember

The VericredMember model maps creates a unique relation between a Member, Vericred group id, and Vericred member id. One is
created for each member and group combination. This model is much more in line with mongo best practices than
VericredCarrierIdMap and also allows us to easily search for members by their Vericred ids.

# Sending Coverage To Vericred

## Updating Subscribers

Before sending any coverage updates to Vericred, we first update the information Vericred has on the subscriber. This is important for
multiple reasons. First, the subscriber may be a new enrollee. In this case, Vericred has no information about the subscriber, and it must
be added to their system. Second, there may be demographic changes or new dependents since subscribers last QLE. In this case, we
need to communicate this information to Vericred first, before we communicate any changes in coverage.

## Qualifying Life Events

In Vericred, all transmissions of coverage are referred to as qualifying life events (QLEs). A qualifying life event corresponds to a set of
SLIs for a subscriber. A QLE is sent to a specific carrier group and coverage period, and can have multiple lines of coverage.

## End-Dating of Coverage

When coverage is ended, whether because of a change in coverage or termination of employment, Rippling is responsible for end-dating
the previous QLEs in Vericred. To do this, Vericred’s subscriber endpoint provides currently active QLEs. We must add an end date to
these coverages, and then send them back to Vericred to inform them of any end dates. Once this is done, we can send in any new
coverage, if there is any, in a new QLE.

# Ingestion

## Ingestion Workflow

When initially ingestion a group we go through the following process, which is accessible through the
VericredAPIDetails.ingest_group endpoint:

1. Create the group on Vericred. Store the group’s id in the VericredCompanyCarrier model
2. Send all domestic work locations for the company to Vericred. The id we receive for each of these is then stored in a
   VericredWorkLocationMap model.
3. Create coverage periods. There may be multiple coverage periods for a carrier if plans do not have matching effective dates. The
   coverage period’s id is then stored in a VericredCompanyCoveragePeriodInfo model. It is also stored on the
   InsuranceCompanyCarrierLineInfo model.
4. Create plans in Vericred. This loads all of the plan information. The vericred plan id is stored on the InsuranceCompanyPlanInfo
   model. If the plan is non-voluntary, it is stored in the vericredId field, and if it is voluntary, it is stored in the vericredVoluntaryId
   field. If a plan has voluntary buy up, it will use both of these fields.
5. Load subscribers to Vericred. Each subscriber and their dependents have their data sent to Vericred. The subscriber id is then stored in
   the VericredCarrierIdMap and VericredMember models.
6. Load coverage via QLEs. Each subscriber has their coverages at the time of ingestion sent to vericred. This is via a QLE, as described
   above. The reason on the QLE here is “initial_enrollment”. If a subscriber has any future QLEs scheduled, we will also send them to
   Vericred at this point. We also include some recently terminated subscribers in this initial ingestion, because some carriers want them.

## Testing Phase

Once ingestion is finished, the group goes into what is considered a “test phase”. This allows the carrier to compare what we have
uploaded in the EDI file with what they already have on record. During this phase, errors are reported by the carrier and must be corrected.
Once the testing phase is passed, the coverage period is approved for production.

## Re-ingestion

When errors are found during the testing phase, we have two ways they can be fixed. First, we can fix each error individually, and send the
corrections to Vericred one by one. This is historically what we have done. The other way is that we can fix errors in Rippling, and then run
the ingestion tool again to send all the corrections at once. This route, which we are calling “re-ingestion” is currently being worked on, and
will soon be available as a tool for ops.

## Dual Communication

During the testing phase for a coverage period, we engage in dual communication mode. While this is active, we send enrollments both by
EDI and by some other method. We send coverages via EDI to keep the file up to date even though it is not yet in production. The other
method, usually email or fax, is what actually updates the carrier, however.

## Renewal of Enrollment

When a company renews their enrollment, a new coverage period has to be created in Vericred. This is done automatically when the first
action is performed using the new CompanyCarrierLineInfo. Our code first checks if a coverage period id exists on a CCLI. If it does not,
then we will create a new one, and use that going forward.

## Vericred Error Tasks

```
EDI Testing Process and Timelines | Vericred Error Tasks
```

# Useful Links:

Vericred API specification: https://app.swaggerhub.com/apis/VericredEnrollments/Enrollments/0.1.2#/

Vericred Documentation: Overview | Ideon - Enrollment
