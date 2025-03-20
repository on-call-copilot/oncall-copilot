import requests
import json

token = 'Bearer b3P8MbaJK86WUZarOxZzAXNfWAd9Hk'

def rippling_api_handler(path: str, params: dict = {}, payload: dict = {}, company_id: str = None, role_id: str = None):
    params_reduced = '&'.join([f'{k}={v}' for k, v in params.items()])
    url = f"https://app.rippling.com{path}?{params_reduced}"

    assert token.startswith('Bearer ')

    headers = {
        'authorization': token,
        'requestedaccesslevel': 'STAFF_USER'
    }

    if role_id:
        headers['role'] = role_id

    if company_id:
        headers['company'] = company_id

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return None

def get_all_carriers_that_require_packets(enrollment_event_id: str, company_id: str, role_id: str):
    """Get all carriers that require packets for a given enrollment event."""
    path = f"/api/insurance/api/company_enrollment_event/{enrollment_event_id}/get_all_carriers_that_require_packets"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)

def get_line_wise_carriers_and_plans_for_event(enrollment_event_id: str, company_id: str, role_id: str):
    """Get line-wise carriers and plans for a given enrollment event."""
    path = f"/api/insurance/api/base_company_enrollment_event/{enrollment_event_id}/get_line_wise_carriers_and_plans_for_event"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)

def get_renewal_details_for_lines_involved(enrollment_event_id: str, company_id: str, role_id: str):
    """Get renewal details for lines involved in an enrollment event."""
    path = f"/api/insurance/api/company_enrollment_event/{enrollment_event_id}/get_renewal_details_for_lines_involved"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)

def get_total_employee_count_for_submission(enrollment_event_id: str, company_id: str, role_id: str):
    """Get total employee count for submission for a given enrollment event."""
    path = f"/api/insurance/api/company_enrollment_event/{enrollment_event_id}/get_total_employee_count_for_submission"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)

def get_selected_eligibility_cclis_for_company_event(company_enrollment_event_id: str, company_id: str, role_id: str):
    """Get selected eligibility cclis for a given company event."""
    path = f"/api/insurance/api/eligibility_company_carrier_line_info/get_selected_eligibility_cclis_for_company_event?companyEnrollmentEventId={company_enrollment_event_id}"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)

def get_total_employee_count_for_submission(company_enrollment_event_id: str, company_id: str, role_id: str):
    """Get total employee count for submission for a given company event."""
    path = f"/api/insurance/api/company_enrollment_event/{company_enrollment_event_id}/get_total_employee_count_for_submission"
    return rippling_api_handler(path, company_id=company_id, role_id=role_id)



print("\nTesting get_all_carriers_that_require_packets:")
print(get_all_carriers_that_require_packets(enrollment_event_id='651c281fd6554f8c0bd8a0ec', company_id='585c512df20db5063607e146', role_id='66bb21feb04ae2fc4ea74c43'))

print("\nTesting get_line_wise_carriers_and_plans_for_event:")
print(get_line_wise_carriers_and_plans_for_event(enrollment_event_id='651c281fd6554f8c0bd8a0ec', company_id='585c512df20db5063607e146', role_id='66bb21feb04ae2fc4ea74c43'))

print("\nTesting get_renewal_details_for_lines_involved:")
print(get_renewal_details_for_lines_involved(enrollment_event_id='651c281fd6554f8c0bd8a0ec', company_id='585c512df20db5063607e146', role_id='66bb21feb04ae2fc4ea74c43'))

print("\nTesting get_total_employee_count_for_submission:")
print(get_total_employee_count_for_submission(enrollment_event_id='651c281fd6554f8c0bd8a0ec', company_id='585c512df20db5063607e146', role_id='66bb21feb04ae2fc4ea74c43'))
