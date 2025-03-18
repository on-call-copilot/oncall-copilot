# Insurance models overview

# Database Schema

## Company Dependent

### Company

Description: Center of Universe.

Relationships:

Has a one-to-many relationship with CompanyInsuranceInfo and CompanyCarrierLineInfo.

### CompanyInsuranceInfo

Description: Repository of company insurance settings.

### CompanyBrokerInfo

Description: Contains insurance broker-related information.

### CompanyCarrierLineInfo

Description:

Collection of entities; backbone of insurance.

Temporally aware.

Relationships:

Connects with Company.

### InsuranceCompanyPlanInfo

Description: Details how insurance plans are offered to the company.

Relationships:

Connects with CompanyCarrierLineInfo.

## Company Independent

### BaseCarrier

Description: Contains insurance company information.

Relationships:

Connects with CompanyCarrierLineInfo.

### InsurancePlan

Description:

Insurance plan related info.

addedBy is null if the plan is generic.

Relationships:

Connects with BaseCarrier.

### Pricing

Description:

Pricing related information.

pricingSet is the Company ID if introduced by the company.

### ServiceArea

Description: Plan geographic mapping.

Relationships:

Connects with RatingArea.

### RatingArea

Description: Pricing for small groups.

Employee Related

### SubscriberLineInfo

Description:

Collection between subscriber and CompanyPlanInfo.

Backbone of EE (Employee Enrollment) side of insurance models.

Temporally aware.

Relationships:

Connects with Subscriber/Member.

### Subscriber/Member

Description: EE & Dependents.

EnrollmentEvent

Description: EE insurance change contextual model.

Relationships:

Connects with SubscriberLineInfo.

### PendingActionGroup

Description:

Collection between EnrollmentEvent and PendingAction.

Carries employee and broker actions.

### PendingAction

Description: Carrier actions.

# Database Models

## Company Independent Core

### BaseCarrier

Represents a Carrier that Insurance works with. Main Attributes: StateCode. CarrierIds.

### InsurancePlan

```
Not directly dependent on company.
Mainly Provided by external Vendors. Vericred. Noyo. Metlife. Beam etc.
NGE team mainly owns this input of external pricing Data into our code.
If pricing entered by company, a pricing model is created and the company ID is stored in “addedBy”
```

### Pricing

```
Not directly dependent on company.
Mainly Provided by external Vendors. Vericred. Noyo. Metlife. Beam etc.
NGE team mainly owns this input of external pricing Data into our code.
If pricing entered by company, a pricing model is created and the company ID is stored in “pricingSet”
PricingChart: Store the actual pricing. Could be a lot of structures. (doc)
```

### RatingArea

```
ACA standardizes the factors that insurance companies can use to calculate premiums for small group rates.
Each state is required to divide up the areas of the state into locations called Rating Areas. When insurance companies price their
premiums, all households within a rating area will have the same adjustment factor applied.
Pricing related
More information provided
```

### ServiceArea

```
Refers to where a plan network is available. Determines whether an employee is able to enroll in a certain plan based on where he/she
is located.
Mostly used for HMO carriers/plans which are limited based on zipcode.
Enrollment eligibility related
```

## Relationships

```
InsuranceCarrier has One to Many Relationship with InsurancePlan[ An Insurance carrier can offer many plans]
InsurancePlan has One to Many Relationship with InsurancePricing[ An Insurance plan can have many pricing depending on Quarter/
zip code etc]
```

## Company Dependent

### CompanyInsuranceInfo

A generic ‘catch-all’ model where we dump a bunch of company insurance settings such as who is the person to sign in BOR letters, do
they want part time employees to be eligible etc.

### InsuranceCompanyCarrierLineInfo (CCLI)

A complicated model. One of the backbones of Insurance.

```
Temporally aware.
This is a basically a unique key on (Carrier, effectiveDate, expirationDate, lineType, Company).
I think of it as representing a contract between a company and carrier for a lineType for a particular duration(effectiveDate &
expirationDate)
Stores things like waiting period/ contribution scheme/ effective date etc.
Relationship: A join between Carrier/company per (lineType, Duration)
```

### InsuranceCompanyPlanInfo

CCLI + InsurancePlan

```
Mostly contains how the company is offering an InsurancePlan to the company.
These are the customizations that a company could do on a plan.
e.g. which set of employees they can offer to.
CCLI has a one to many relationship to InsuranceCompanyPlanInfo
There will be at least one entry per CCLI
```

### CompanyEnrollmentEvent

```
There are many types of events here. Whenever a major company wide insurance change happens, we create this event.
Inherit from RPDocumentWithoutRole, this event is a company level event
Eg: When a company is transferring insurance to Rippling we create a BORCompanyEnrollmentEvent
When a company is shopping Insurance[NGE flow] we create a CompanyEnrollmentEvent, with
reason=”NEW_GROUP_ENROLLMENT”.
When a company is renewing its contract yearly or changing their contracts, we create CompanyEnrollmentEvent, with
reason=”OPEN_ENROLLMENT”
```

## Employee Related

### SubscriberLineInfo

For each line of Insurance, the employee can make selections about their Insurance. Together, these would form a continuous timeline.
For each line, we store this in a model called SubscriberLineInfo.

Commonly abbreviated as sli.

SLI is temporally aware model.

Main Attributes:

```
EffectiveDate + ExpirationDate
ChosenPlan → Optional[InsuranceCompanyPlan]
chosenDependents → List[Members]
lineType → the Linetype
EnrollmentEvent → A reference to the Event which caused the creation of this SLI
```

A new SLI is created only when there is an occasion to do so(an event). This is called an EnrollmentEvent.

Usually, an employee’s first SLI is created due to a NewHireEnrollmentEvent. Every year during open enrollment a new SLI is created due
to an OpenEnrollmentEvent(which in turn is created due to an CompanyEnrollmentEvent). New slis might also be created due to, QLE. or
Termination or Cobra.

Events might affect a change in insurance coverage(and creation of SLIs) for only _some_ lines of coverage. Eg: An QLE might result only
new selections available for Medical/Dental and Vision.

Note: Even if an employee doesn’t change their elections. A new sli means, there was an option for changing the Insurance coverage of an
employee

### EnrollmentEvent

Enrollment creation is governed by complicated logic explained <link here>.

```
Each different kind of enrollment has implement the following functions
getEffectiveDate(self, companyCarrierLineInfo)
This gives the effective date of the insurance for this ccli. THIS IS TIME INDEPENDENT.
getDeadline()
Deadline to enroll in Insurance. might want to do it earlier than the absolute last minute. Especially for OE/NGE.
getEnrollmentLimitDate(self, companyCarrierLineInfo) → This give the last date carrier would accept insurance enrollment.
Usually, effective-date + 30 days. ALSO TIME INDEPENDENT.
getReferenceDate()
Reference date
isAvailableForEmployee(ccli, referenceDate)
Is the plan offered by CCLI available to the employee on the given date.
Common Enrollment Event Functions
getAvailableCCLIs()
getAvailablePlans()
manageNotificationLifeCycle()
OpenEnrollmentEvent Inherit from RPDocumentWithRole, which is a role level event
```

## Carrier transmissions/Benefits marketplace integrations related

### PendingActionGroup

Whenever, an EnrollmentEvent is finalized. AKA, when an employee makes all the insurance selections available to them, we create a
PendingActionGroup (through a on_change hooked function EnrollmentEvent.onFinalized()). This is co-ordinator model which
coordinates all the communication to the carriers about the employee insurance selections.
The co-ordination function is process().

Common abbreviation: pag.

### PendingAction

For each carrier we _might_ have to communicate the employee details, we create a pendingAction, the initial status is “INIT”

PendingActionGroup has one-to-many relationship with PendingAction.

On PendingActionGroup.process(), we try to fill the employee selections in forms. If we are successful, we set the status of PA to
“PROCESSED”.

PendingAction has two extremely important functions.

a) shouldPerformAction: Decides if we need to communicate the enrollment information to the insurance carrier.

b) performAction: Actually performs the action and communicates information to the carrier.

```
Actual communication logic is more complicated and changes too much to put in writing. Best is to look at tests or the code itself.
```
