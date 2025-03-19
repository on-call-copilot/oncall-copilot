# ETA appendix

**ingestVericredGroup**
This ETA ingests the entirety of a group to Vericred. This is called by the either by the frontend when ops ingests a group, or by other ETAs
that ingest groups automatically
**updateClassificationVericredIdIfNeeded**
updates vericred information for a classification in Rippling’s system. This is called via an on change in the Carrier Classification model,
when the type or value fields of the classification changes.
**push_all_subscriber_data_to_vericred**
updates all demographic information and carrier classifications. This is triggered from the frontend by ops when they want to push over
data on carrier classification sets
**reingest_enrollment_data_for_company_to_vericred**
This reingests all current and future qles for a company to vericred. This is triggered on the frontend by the ops team when they want to
reingest groups that are in testing
**clear_vericred_info_from_company**
this removes all vericred info for a company. It is only used via webscript when vericred was set up incorrectly.
**update_vericred_company_coverage_period_info**
this caches information about coverage periods from vericred into the VericredCompanyCoveragePeriodInfo model. This runs
automatically every hour, so the coverage periods should always be in sync.
**update_all_vericred_error_tasks**
Pulls new information about vericred errors from vericred, and puts them into the insurance task system. This runs automatically every six
hours, and thus tasks are updated multiple times a day. This will also pull any comments on errors from vericred as well.
**auto_ingest_bor_vericred_groups**
This will ingest some BOR groups to vericred automatically. Currently, this happens for the carriers Anthem, Cigna, Kaiser, BCBS MA,
Oxford, and UHC. This happens automatically once a week.
**auto_ingest_sequoia_groups_to_vericred**
This will automatically ingest Sequoia Tech Trust BOB groups to Vericred. This happens automatically once a day


