# Insurance basics overview

# Basics of Insurance

## Health Insurance

Health insurance is a contract between the employee and health insurance carrier. Employees who sign up for health insurance have
discounted prices when they go to the doctor.
For example, if a person gets a blood test at a doctor without health insurance, they could be charged around $400 for that test. However,
a person with insurance would only be charged $20-$50 depending on their plan. The remaining cost is covered by the carrier. That is why
the Insurance industry is so important. Without Insurance, regular employees could not afford to go to the doctor.

## Health Insurance Carriers

Carriers are the companies that make plans and sell them to employers and individuals. Examples of these would be Kaiser Permante,
Blue Cross, Aetna, Guardian, Metlife. They are liable for the cost of the majority of the doctor procedures and establish the rates to charge
for plans. They also create _health insurance plans_.

## Health Insurance Plans

Each carrier has multiple differing health insurance plans. Plans have different attributes such as a _deductible_ , _copay_ , _out-of-pocket-
maximum_ , and _coinsurance_. These terms typically have to do with how much an individual will have to pay for specific treatments. Each
plan is priced differently based on how favorable the attributes are of the plan. These are categorized into metal tiers: Platinum, Gold,
Silver. Bronze.
Platinum plans have the best attributes for individuals while being the most expensive, and Bronze plans having the worst attributes but
are the cheapest. For example, a Platinum plan might have a $0 copay while a Bronze plan might have a $50 copay, so if the subscriber
goes for a check-up they either get that specific treatment free and have to pay $50 for the services but each month they would be paying
more for the platinum plan.

## Brokers

In the United States, in order for a group to buy insurance (with some small exceptions), the company will need to have plans sold to them
by Brokers. Brokers are individuals who have accrued a certain amount of hours of coursework and taken a test in order to understand the
ins-and-outs of the insurance industry.
Brokers do not get paid by the employers. Instead they take a percentage (typically 5%) of the premiums paid to the carrier on all enrolled
employees. In Rippling’s case, **Rippling Insurance Services, Inc** (also known as Waveling Insurance Services) will be the broker for a
majority of our internal clients.
Rippling allows companies to bring their own broker to the Rippling platform. Thus, Rippling Insurance Services will not be the broker of
record for that group and we will not be paid by the Insurance Carrier. The Broker will need to make the changes for the group.
Brokers are also referred to as _broker of record_.

```
Group Health Insurance is another way to refer to a health insurance plan. A group's members are usually comprised of company
employees or members of an organization. Rippling insurance always applies to groups.
```

```
The term broker of record has two meanings. The first is referring to the role of broker as described above. The second will be
detailed below.
```

### Broker of Record (BoR)

```
This is the broker or brokerage that can make changes to the company’s insurance options (not underlying plan) and can send
changes regarding the employees group. The Broker of Record is also paid a percentage fee of the total premiums paid by the group
to the carrier. Rippling Insurance Services is the broker of record for our internal clients.
A BOR group is one where Rippling is the insurance broker for the group. In general, this means we automatically manage forms for
the group, including automatically creating some API or EDI connections. If a group is a BOR group, then the field
enrollmentManagerType on the CompanyBrokerInfo object will be set to RIPPLING. However, also note that there are a few
different types of BOR groups, with some caveats
```

### Bring Your Own Broker (BoB)

```
A BOB group is one where the group uses a broker other than rippling. If a group is a BOB group, then the field
enrollmentManagerType on the CompanyBrokerInfo object will be set to BROKER. In general, we do not send any forms or
enrollments for BOB groups. However, BOB groups can pay to have Rippling manage forms. In this case,
isRipplingManagingForms on the CompanyInsuranceInfo object will return true. Once Rippling is managing forms, the broker can
also chose to connect some groups with EDI or API.
```

### NFP

Rippling Insurance Services sometimes partners with another brokerage on some of our groups, NFP. NFP has the resources to advise
the groups of a specific size on their renewals as we do not have many internal brokers within Rippling Insurance Services. The NFP
brokers will advise our clients on what plans to choose and will walk the groups through their renewals. We will still be listed as the broker
of record on these groups but NFP gets a percentage of our commissions.

### Waveling Only Groups

Waveling in the name of Rippling’s Insurance Brokerage. BOR groups with WAVELING_ONLY in the nfpStatus field on their
CompanyBrokerInfo are managed solely by Waveling, and are pure BOR.

### Waveling Plus NFP Groups

NFP is an outside brokerage that Rippling collaborates with to manage some BOR groups. BOR groups with WAVELING_PLUS_NFPin the
nfpStatus field on their CompanyBrokerInfo are managed primarily by Waveling, with some assistance from NFP. For the sake of
carrier connections, we can still treat this as a BOR group.

### NFP Plus Waveling Groups

These groups are primarily managed by NFP, with some assistance from Waveling. These groups have NFP_PLUS_WAVELING in the
nfpStatus field on their CompanyBrokerInfo. For these groups, we should treat them as if they are BOB groups, as NFP has most of
the responsibilities. It is still the case that enrollmentManagerType is listed as RIPPLING, however.

## Distinguishing BOB and BOR Groups

Because of the existence of NFP Plus Waveling groups, we can not use the enrollmentManagerType field to distinguish between BOB
and BOR groups. Rather, we should use the isRipplingBroker property on the CompanyInsuranceInfo model to check this, as it
checks for these edge cases. If this property is true, then the group is BOR, else it is BOB

## Premiums

Premiums are what the group pays to the carrier for Insurance. Each employee and dependent has a premium cost per month which is
based on age, plan and zip code of the group. Employees typically pay a percentage of the premium that the company owes (companies
are required to pay at least 51% by the ACA).
For example, a company with one employee might owe the carrier $400 per month for the insurance plan. The group offers to _contribute_
75% ($300) of this payment on behalf of the employee so the employee will owe 25% ($100) for insurance.

## Contributions

As seen in the above example, companies have to contribute toward the cost of Insurance for employees. Companies often choose a
percentage to contribute. Continuing the example, our Payroll system will hold that $100 from the employee’s paycheck. In turn the group
will pay the full amount to the carrier for the premium, but the premiums that the employees “paid” will just be held in their bank account.

## Insurance Operations Key Terms

### New Hire Enrollment (NHE)

When an employee is hired to a company, they have their first opportunity to apply for coverage. The employee will enter their information
and plan selection into Rippling and then we will send this information to the carrier. If the employee does not make any elections by a
certain time period, they will not be able to apply for insurance until they experience a Qualifying Event or until their company’s Open
Enrollment.

### Qualifying Life Event (QLE)

This is an event that happens to either an employee or one of the employee’s dependents. Examples include
getting married
losing coverage elsewhere
having a baby
When this event occurs to the subscriber or a dependent, the subscriber can make specific changes to the plan selection, enroll in
coverage for the first time or add/remove dependents from coverage.

### Open Enrollment (OE) / Renewal

These two terms are interchangeable. Like NHE and QLE, this is another opportunity the subscriber can change health insurance
elections with the carrier. Once a year, a company will go through Open Enrollment where they can choose new plans for the entire group
and then the employees have an opportunity to enroll. An open enrollment only occurs if the company had coverage for the past year.

### New Group Enrollment (NGE)

Soon after a company gets their first salaried, full-time employee, the group will want to enroll in health insurance. To enroll in health
insurance, the group as a whole has to prove to the carriers that they are a legitimate company recognized by the state and that they are
currently paying their employees through payroll.
The carrier will provide plans and rates based on their location. Each carrier has specific underwriting guidelines (or _rules_ ) which tell if a
group will be eligible for their plans. Once the carrier has decided a group is approved for a plan, then those employees will get coverage.

### Subscriber and Dependents

Relative to insurance, an employee is known as the _subscriber_. The _dependents_ of a subscriber include:
Children
Spouse or domestic partner

### COBRA

If a group is above 20 employees, they are eligible for the federal program _COBRA_. This allows for terminated employees to choose to
continue coverage on the group’s plan that they were terminated from. The employee often has to pay the full price of the plan (no
contribution) plus a 2% administrative fee.
Companies have the chance to contribute to the price of the COBRA coverage but are not required to as is the case with the regular
insurance plans offered to active employees. Rippling manages the COBRA coverage for companies which are eligible for COBRA
coverage, but we do not manage it for groups under 20 employees. There is a different process for these smaller groups per state which is
why we do not manage this.

### Waiting Period

This is the period of time before a new member can be effective. The group sets a waiting period for all of their new hires. The “first of the
month following hire date” is a common waiting period.
For example, an employee who was hired on April 7th, will have their insurance effective on the first of the following month, May 1st.

### Effective Date

This is the date in which coverage begins or ends for an employee or group with the health insurance carrier. Most effective dates are on
the first of the month. Examples:
A new hire whose first day is on May 5th will have coverage effective on June 1st.
A group that enrolled in coverage in mid-October may apply for coverage to be effective starting November 1st.
The yearly renewal for a company is August 1st and that is when their plan changes and employee’s new elections will be effective.
A termination that occurred on November 15th may have a cancellation effective date with the carrier of November 30th, the last day of
November.

### Benefits Administrator / Administration (BenAdmin)

Rippling, as described above, has brokers who are both BoR and BOB. However, regardless of which type of broker, as a BenAdmin
system we will populate the forms for the broker, display the plans for the employees and manage the payroll deductions for the broker
and group.

### Terminations

Once an employee leaves the company, the group also has to terminate the subscriber from the insurance carrier. Thus, in Rippling when
an admin terminates an employee, we will create a task to cancel this coverage with the carrier.

### Forms

In order to enroll employees onto health insurance plans, carriers require enrollment forms filled out with specific information. These forms
are different for each carrier but typically require the same information. This includes SSN, Date of Birth, plan selection, name, address,
and dependents who need to be enrolled. Rippling populates the information captured into our system and prints it on forms which we
automatically send to carriers.

### EDI / API

Besides forms, carriers also utilize APIs and EDI feeds. These are two completely automated feeds between the Rippling system and the
carrier system. Thus, no transactions are sent to the carrier as information input into the Rippling system is passed to the carrier directly
without having to send a form.

### Lines of Coverage

_Lines of coverage_ are the types of insurance that a company offers. Most groups offer more than one type of coverage. Most common
examples:
**Medical (Health)**
This is a typical doctor appointment in terms of ailments with the body such as being sick, needing surgery or common wellness checks
**Dental (Ancillary)**
This is insurance that covers anything that has to do with the mouth and teeth well-being
**Vision (Ancillary)**
This is insurance that covers anything related to the eyes and vision.

```
The term admin is used throughout documentation, conversations and code here at Rippling. The terms benefits administrator and
admin are synonymous.
```

**Basic Life (Ancillary)**
This is coverage that every employee of the group gets automatically as the group pays for the plan entirely. This covers funeral
expenses in the instance of death
**Voluntary Life (Ancillary)**
This is coverage that employees can choose to enroll in and pay for if they want to get additional coverage in terms of the amount paid
out for life insurance.
**Short term Disability - STD (Ancillary)**
This covers short term disabilities.
**Long term Disability - LTD (Ancillary)**
This covers short term disabilities.
