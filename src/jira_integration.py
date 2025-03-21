import os
import dotenv
import requests
import re
import argparse
from urllib.parse import urlparse
import json
from jira import JIRA
import logging
from typing import Optional, Dict

logger = logging.getLogger('bartender_api')

class JiraIntegrator:
    def __init__(self):
        self.jira = None
        self.setup_jira()
        dotenv.load_dotenv()

    def markdown_to_adf(self, markdown_text):
        """
        Convert Markdown to Atlassian Document Format (ADF)
        This function uses the Atlassian Document Format converter API
        to transform markdown into ADF JSON structure.
        """
        # Option 1: Use Atlassian's Cloud API (if you have access)
        url = "https://api.atlassian.com/document/converter"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "sourceFormat": "markdown",
            "targetFormat": "adf", 
            "content": markdown_text
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error converting Markdown to ADF: {e}")
            # If API fails, use the manual conversion fallback below
            return self.manual_markdown_to_adf(markdown_text)


    def manual_markdown_to_adf(self, markdown_text):
        """
        A simplified manual conversion of Markdown to ADF.
        This is not comprehensive but handles basic Markdown elements.
        """
        import re
        
        # Initialize the ADF document structure
        adf = {
            "version": 1,
            "type": "doc",
            "content": []
        }
        
        # Split the markdown by lines
        lines = markdown_text.split('\n')
        current_paragraph = None
        in_list = False
        list_items = []
        
        for line in lines:
            # Handle headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
                
                adf["content"].append({
                    "type": "heading",
                    "attrs": {"level": level},
                    "content": [{"type": "text", "text": heading_text}]
                })
                continue
                
            # Handle bullet lists
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                list_text = line.strip()[2:]
                if not in_list:
                    in_list = True
                    list_items = []
                
                list_items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": list_text}]
                    }]
                })
                continue
            elif in_list and line.strip() == '':
                # End of list
                adf["content"].append({
                    "type": "bulletList",
                    "content": list_items
                })
                in_list = False
                list_items = []
                continue
                
            # Handle code blocks (simple version)
            if line.strip().startswith('```'):
                # We'll skip full code block handling for simplicity
                continue
                
            # Handle bold and italic (simplified)
            # This is much more complex in reality and would need a proper parser
            
            # Handle paragraphs (anything else)
            if line.strip():
                # Process inline formatting (bold, italic, links)
                # This is simplified for demonstration
                
                # Bold text: **text** or __text__
                bold_pattern = r'\*\*(.*?)\*\*|__(.*?)__'
                # Italic text: *text* or _text_
                italic_pattern = r'\*(.*?)\*|_(.*?)_'
                # Links: [text](url)
                link_pattern = r'\[(.*?)\]\((.*?)\)'
                
                # For simplicity, we're just adding the line as plain text
                # A real implementation would parse these inline elements
                
                adf["content"].append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}]
                })
        
        # Handle any remaining list
        if in_list:
            adf["content"].append({
                "type": "bulletList",
                "content": list_items
            })
        
        return adf


    def plain_text_to_markdown(self, text):
        # Add simple Markdown formatting
        # Headers (lines ending with colon)
        text = re.sub(r'^(.+):$', r'## \1', text, flags=re.MULTILINE)
        
        # Auto-detect URLs and convert to links
        url_pattern = r'https?://[^\s]+'
        text = re.sub(url_pattern, lambda m: f'[{m.group(0)}]({m.group(0)})', text)
        
        # Format paragraphs properly
        paragraphs = re.split(r'\n\s*\n', text)
        return '\n\n'.join(paragraphs)

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

        comment_text = f"""
        ```
        {comment_text}
        ```
        """
        
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
        
        # Prepare the comment payload (using Jira API 3.0 format)
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment_text
                            }
                        ]
                    }
                ]
            }
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
    # Set up argument parser
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