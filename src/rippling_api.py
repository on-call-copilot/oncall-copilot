import os
import dotenv
import requests
import json


class RipplingApiHandler:
    def __init__(self):
        """Initialize the RipplingApiHandler with authentication details."""
        dotenv.load_dotenv()
            
        self.token = os.getenv("TOKEN")
        self.role_id = os.getenv("ROLE_ID")
        self.company_id = os.getenv("COMPANY_ID")

    def _make_request(self, path: str, params: dict = None, payload: dict = None):
        """Internal method to make API requests to Rippling.
        
        Args:
            path (str): The API endpoint path
            params (dict): Query parameters
            payload (dict): Request payload
            override_company_id (str): Optional company ID to override the default
        """
        params = params or {}
        payload = payload or {}
        params_reduced = '&'.join([f'{k}={v}' for k, v in params.items()])
        url = f"https://app.rippling.com{path}?{params_reduced}"

        headers = {
            'authorization': self.token,
            'requestedaccesslevel': 'STAFF_USER'
        }

        if self.role_id:
            headers['role'] = self.role_id

        if self.company_id:
            headers['company'] = self.company_id

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return None

    def get_noyo_company_plan_info(self, company_id: str, company_plan_info_id: str = None):
        """Get noyo company plan info objects for a given company.
        
        Args:
            company_id (str): Optional company ID to override the default
        """
        path = "/api/insurance/api/noyo_company_plan_info/"

        payload = {
            'company': company_id,
        }
        if company_plan_info_id:
            payload['company_plan_info'] = company_plan_info_id
        return self._make_request(
            path, 
            params=payload,
        )

    def get_custom_communication_detail(self, company_id: str):
        """Get custom communication detail objects for a given company.
        
        Args:
            company_id (str): company ID to override the default
        """
        path = "/api/insurance/api/custom_communication_detail/"
        return self._make_request(
            path, 
            params={'company': company_id},
        )


if __name__ == "__main__":
    dotenv.load_dotenv()
    handler = RipplingApiHandler()
    
    # Example usage
    print(handler.get_noyo_company_plan_info('637545f1a3a2c9c8f4adef54'))
    print(handler.get_custom_communication_detail('6218e901df1a3783f80b0002'))