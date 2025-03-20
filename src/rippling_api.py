import requests

def rippling_api_handler(token: str, path: str, payload: dict = {}, company_id: str = None, role_id: str = None):

    headers = {
        'authorization': token,
        'requestedaccesslevel': 'STAFF_USER'
    }

    if role_id:
        headers['role'] = role_id

    if company_id:
        headers['company'] = company_id

    return requests.request("GET", path, headers=headers, data=payload).text




def make_api_calls(company_id: str, role_id: str, token: str):

    response_line_configuration = rippling_api_handler(
        token=token,
        path='https://app.rippling.com/api/insurance/api/line_configuration/all_line_infos',
        company_id=company_id,
        role_id=role_id,
    )

    print(response_line_configuration)

    response_companies = rippling_api_handler(
        token=token,
        path='https://app.rippling.com/api/hub/api/companies/?large_get_query=true',
        company_id=company_id,
        role_id=role_id,
    )

    print(response_companies)

    response_company_insurance_info = rippling_api_handler(
        token=token,
        path='https://app.rippling.com/api/insurance/api/company_insurance_info/?large_get_query=true',
        company_id=company_id,
        role_id=role_id,
    )

    print(response_company_insurance_info)

    response_carrier = rippling_api_handler(
        token=token,
        path='https://app.rippling.com/api/insurance/api/carrier/583fdf270971c5546929c869',
        company_id=company_id,
        role_id=role_id,
    )

    print(response_carrier)

    response_eligibility_company_carrier_line_info = rippling_api_handler(
        token=token,
        path='https://app.rippling.com/api/insurance/api/eligibility_company_carrier_line_info/get_selected_eligibility_cclis_for_company_event?companyEnrollmentEventId=651c281fd6554f8c0bd8a0ec',
        company_id=company_id,
        role_id=role_id,
    )

    print(response_eligibility_company_carrier_line_info)




if __name__ == "__main__":
    company_id = ['585c512df20db5063607e146']
    role_id = ['66bb21feb04ae2fc4ea74c43']
    token = ['Bearer b3P8MbaJK86WUZarOxZzAXNfWAd9Hk']
    for i, _ in enumerate(company_id):
        print(make_api_calls(company_id[i], role_id[i], token[i]))