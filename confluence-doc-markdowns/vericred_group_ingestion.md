# Vericred Group Ingestion

When a group is connected to Vericred, the first thing we need to do is ingest the entire group structure. This document goes over
everything that needs to be ingested. The entry point for this ingestion is VericredAPIDetails().ingest_group(), and this goes through
each component of what this function does.
Also, note that this ingestion is idempotent. Once an object in our system is ingested, if we run ingestion again, we will see that it was
already ingested, and skip over trying to re-ingest, moving onto the next step. This is useful if an ingestion errors out, so we can fix the
issue, then just run ingestion again.
1. Create Group
This is done in the VericredAPIDetails().get_or_create_group() method. First, we need to send data about the group overall to
vericred. This includes company tax info (such as EIN, Legal name, and SIC Code), number of employees, and headquarters address. If
group IDs are missing from the CCLIs for the group, or if the HQ address is not available, this will fail. Group information is sent to vericred
by POSTing to the /groups URL. When we obtain a response, we save the Group ID by creating a VericredCompanyCarrier model for
the group. We also create a VericredWorkLocationMap model for the HQ location, as it is also assigned an id via this operation.
2. Create Work Locations
This is done by calling VericredAPI.get_or_create_work_location() on each domestic work location for the company. A work location
that is sent to Vericred consists of an address and a flag for being remote or physical. This is sent to Vericred via POSTing to the
/groups/{group_id}/locations URL. When we get a response back, we save the work location id in a VericredWorkLocationMap
model
3. Create Coverage Periods
This is done by calling VericredAPIDetails.get_or_create_coverage_period(). We attempt to create a coverage period for each
CCLI. If two CCLIs have the same carrier, group id, and start and end dates, we will just assign them to the same coverage period. A
coverage period includes start and end dates for the coverage year, waiting period information, and the name of the carrier. We also
transmit information about who the broker is and if the group is a part of the PEO. This is sent to vericred using the
/groups/{group_id}/coverage_periods URL. When we get a response, we store the coverage period id in two places. First, we store is
on the CCLI. Second, we create a VericredCompanyCoveragePeriodInfo model. This model includes much metadata about the coverage
period that is created by Vericred.
4. Create Plans
This is done by calling VericredAPIDetails.get_or_create_plan() for each plan. The plan object we sent to vericred has a name,
identifier, and some info for things like optional buy up on ancillary plans. This is sent over to Vericred using the
/coverage_periods/{coverage_period_id}/plans URL. When we get a plan ID back, we store it one of two places. For most plans,
this is stored in the vericredId field of the InsuranceCompanyPlanInfo model. For voluntary buy up plans, it is instead stored in the
vericredVoluntaryId field of the same model. The reason for this is because some plans (such as life with a voluntary buy-up) have to be
represented as two separate plans in vericred (one for the base plan, and one for the buy up). This allows us to send over both, as
needed.
5. Completing Coverage Period Set Up
Once all plans have been ingested, Vericred has us call /coverage_periods/{coverage_period_id}/complete_setup. This locks in the
coverage period information, and signals to them that they can start processing and mapping the plans we have sent. At this point, we
cannot change anything on the coverage period object in Vericred. We can, however, still add more plans to a coverage period if the need
arises.


6. Create Subscribers and Dependents
For each role that has present or future coverage for the carrier, we will next ingest them and their dependents. This is done in the method
VericredAPI.create_or_update_subscriber(). All members that are sent to vericred have all relevant demographic fields for insurance
enrollments. Subscribers are passed with information about employment, including salary, start and end dates, and employment type.
Subscribers are initially passed to the /groups/{group_id}/subscribers endpoint, and dependents are passed to the
/subscribers/{subscriber_id}/dependents endpoint.
7. Load Coverages via QLE
For each role that was ingested, we call VericredInitialIngestionManager.generate_and_push_data(). This allows us to ingest
current and future coverage to vericred. The block that does this is wrapped in a try / except statement, and any errors in this ingestion are
gathered into a report. This is emailed out at the end of this process if any errors are found.


