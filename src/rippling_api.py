import requests

def rippling_api_handler(token: str, path: str, params: dict = {}, payload: dict = {}, company_id: str = None, role_id: str = None):
    params_reduced = '&'.join([f'{k}={v}' for k, v in params.items()])
    url = f"https://app.rippling.com{path}?{params_reduced}"

    assert token.startswith('Bearer ')

    headers = {
        'authorization': token,
        'requestedaccesslevel': 'STAFF_USER'
    }

    print(url)

    if role_id:
        headers['role'] = role_id

    if company_id:
        headers['company'] = company_id

    return requests.request("GET", url, headers=headers, data=payload).text

# rippling_api_handler(
#     token='Bearer nVBS4zBnZhaRVvzNecV0HdSKp8C3UO',
#     path='/api/insurance/api/carrier_connection_admin/get_carrier_connection_details',
#     company_id='585c512df20db5063607e146',
#     role_id='66bb21feb04ae2fc4ea74c43',
#     params={
#         'companyId': '585c512df20db5063607e146',
#         'carrierConnectionId': '66bb21feb04ae2fc4ea74c43'
#     }
# )