import os
import subprocess
import dotenv
import requests
import re
import argparse
from urllib.parse import urlparse
import json
from jira import JIRA
import logging
from typing import Optional, Dict

from markdown_to_adf import markdown_to_adf

logger = logging.getLogger('bartender_api')

node_script_path = os.path.join(os.path.dirname(__file__), 'md-to-adf-test/test.js')
class JiraIntegrator:
    def __init__(self):
        self.jira = None
        self.setup_jira()
        dotenv.load_dotenv()
   
    def setup_jira(self):
        """Initialize Jira client with credentials from environment variables"""
        try:
            dotenv.load_dotenv()
            jira_email = os.getenv('JIRA_EMAIL')
            jira_api_token = os.getenv('JIRA_API_TOKEN')
            jira_server = os.getenv('JIRA_SERVER')  # e.g., "https://your-domain.atlassian.net"

            if not all([jira_email, jira_api_token, jira_server]):
                raise ValueError("Missing Jira credentials in environment variables")

            self.jira = JIRA(
                basic_auth=(jira_email, jira_api_token),
                server=jira_server
            )
            logger.info("Jira client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {str(e)}", exc_info=True)
            raise

    def extract_issue_key(self, jira_url: str) -> Optional[str]:
        """Extract the issue key from a Jira URL"""
        try:
            # Match patterns like "PROJECT-123" in the URL
            pattern = r'[A-Z]+-\d+'
            match = re.search(pattern, jira_url)
            if match:
                return match.group(0)
            logger.warning(f"Could not extract issue key from URL: {jira_url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting issue key from URL: {str(e)}", exc_info=True)
            return None

    def get_issue_details(self, jira_url: str) -> Dict:
        """Fetch issue details from Jira given a URL"""
        try:
            issue_key = self.extract_issue_key(jira_url)
            if not issue_key:
                raise ValueError(f"Invalid Jira URL: {jira_url}")

            logger.info(f"Fetching details for Jira issue: {issue_key}")
            issue = self.jira.issue(issue_key)
            fields = self.jira.fields()
            

            # Extract relevant information
            issue_details = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "issue_type": issue.fields.issuetype.name,
                "priority": issue.fields.priority.name if issue.fields.priority else None,
                "reporter": {
                    "name": issue.fields.reporter.displayName,
                    "email": issue.fields.reporter.emailAddress
                } if issue.fields.reporter else None,
                "assignee": {
                    "name": issue.fields.assignee.displayName,
                    "email": issue.fields.assignee.emailAddress
                } if issue.fields.assignee else None,
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "labels": issue.fields.labels,
                "companyId": issue.fields.customfield_10046,
                "roleId": issue.fields.customfield_10047

            }

            logger.debug(f"Successfully fetched details for issue {issue_key}")
            return issue_details

        except Exception as e:
            logger.error(f"Error fetching Jira issue details: {str(e)}", exc_info=True)
            raise


    def post_jira_comment(self, ticket_url:str, comment_text:str, username:Optional[str]=None, api_token:Optional[str]=None):
        """
        Post a comment to a Jira issue.
        
        Args:
            jira_url (str): URL of the Jira issue
            comment_text (str): Text of the comment to post
            username (str, optional): Jira username/email
            api_token (str, optional): Jira API token
        
        Returns:
            dict: Response from the Jira API
        """
        # Extract the Jira domain from the URL
        parsed_url = urlparse(ticket_url)
        jira_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Extract the issue key from the URL
        issue_key = self.extract_issue_key(ticket_url)
        
        # If credentials are not provided, prompt for them
        if not username:
            username = os.getenv("JIRA_EMAIL")
        
        if not api_token:
            dotenv.load_dotenv()
            api_token = os.getenv("JIRA_API_TOKEN")
        
        # Construct the API endpoint for adding a comment
        api_endpoint = f"{jira_domain}/rest/api/3/issue/{issue_key}/comment"
        
        # Prepare the headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        adf_comment = markdown_to_adf(comment_text)
        
        # Prepare the comment payload (using Jira API 3.0 format)
        payload = {
            "body": adf_comment
        }

        
        # Make the API request with Basic Authentication
        response = requests.post(
            api_endpoint,
            json=payload,
            headers=headers,
            auth=(username, api_token)
        )
        
        # Check if the request was successful
        if response.status_code == 201:
            print(f"Comment successfully posted to {issue_key}: {ticket_url}")
            return response.json()
        else:
            print(f"Failed to post comment. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Post a comment to a Jira issue')
    parser.add_argument('jira_url', help='URL of the Jira issue')
    parser.add_argument('comment', help='Comment text to post')
    
    # Parse arguments
    args = parser.parse_args()
    jira_integrator = JiraIntegrator()
    
    # Post the comment
    try:
        result = jira_integrator.post_jira_comment(args.jira_url, args.comment)
        if result:
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")