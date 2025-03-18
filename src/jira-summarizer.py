import json
import os
from openai import OpenAI
import time
from typing import Dict, List, Any


# Define system prompt as a separate variable
def get_system_prompt() -> str:
    """Get the system prompt with insurance basics overview."""
    insurance_basics = read_markdown_file("confluence-doc-markdowns/insurance_basics_overview.md")
    insurance_models = read_markdown_file("confluence-doc-markdowns/insurance_models_overview.md")
    vericred_integration = read_markdown_file("confluence-doc-markdowns/vericred_integration.md")
    jira_ticket_format = read_markdown_file("jira-ticket-format.json")

    return f"""
You are a developer in Benefits Marketplace Integrations team in Rippling.
Rippling is a company selling HR products to other companies. These companies will have admin and employee. Admins are employee who have admin privileges.
One of the products rippling offers is insurance in US
Your team works on transmitting insurance benefits selected by an employee to the insurer company(called carriers internally) via some third party vendors and inhouse solutions.
We work with following vendors for transmitting insurance benefits:
1. Noyo
2. Vericred also referred to as ideon 
3. One-Konnect also referred to as Ebn 
4. In-house solution called Stedi

Admin selects lines, insurance plans, payment from cataloged plans in rippling which maps to some plans in the carrier's/vendor's catalog.
Then employee selects the plans they want to buy, and the Benefits Marketplace Integrations team transmits the benefits to the carrier.
Here is the detailed documentation and information about the whole process:

Insurance basics overview:
{insurance_basics}

Insurance models overview:
{insurance_models}

Vericred integration:
{vericred_integration}

You are also an expert at analyzing Jira tickets and extracting key information. 

The Jira tickets follow this JSON format:
{jira_ticket_format}

Pay special attention to the description, comments, and RCA fields as they often contain the most relevant information about the issue.

Analyze the Jira ticket given by user, read all the content, description, comments, etc. and understand the issue user was facing and the detailed reason 
due to which the issue occured:
    1. A concise summary of the issue(problem faced and the reason due to which the issue occurred don't include the solution)
    2. A list of linked issues mentioned in the content
    
    For linked issues, look for:
    - Issue IDs in the format of PROJECT-NUMBER (e.g. BENINTEG-4373, BENPNP-123, BENEX-456)
    - URLs of format https://rippling.atlassian.net that contain issue IDs like https://rippling.atlassian.net/browse/BENINTEG-2529
    - Extract only the issue ID (e.g. BENINTEG-2529) from these URLs
    - Common project prefixes include BENINTEG, BENPNP, BENEX, but there may be others
    
    Format your response exactly as follows:
    ```json
        "summary": "Your summary of the ticket issue here",
        "linked_issues": ["BENINTEG-123", "BENPNP-456", ...]
    ```
    
    If no linked issues are found, return an empty list.
"""

# Initialize the OpenAI client
client = OpenAI(api_key="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")

def read_markdown_file(file_path: str) -> str:
    """
    Read a markdown file and return its contents as a string.
    
    Args:
        file_path (str): Path to the markdown file
        
    Returns:
        str: The contents of the markdown file as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading markdown file {file_path}: {e}")
        return ""


def read_jira_data(file_path: str) -> List[Dict[str, Any]]:
    """Read Jira data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading Jira data file: {e}")
        return []

def create_prompt_for_ticket(ticket: Dict[str, Any]) -> str:
    """Create a prompt for OpenAI based on the ticket data."""
    prompt = f"""
    Analyze the following Jira ticket:
    
    Jira Ticket:
    {json.dumps(ticket, indent=2)}
    """
    return prompt

def process_ticket_with_openai(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Process a ticket with OpenAI to get summary and linked issues."""
    prompt = create_prompt_for_ticket(ticket)
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # You can adjust the model as needed
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content.strip()
        print(f"Processing ticket {ticket.get('key', 'Unknown')}")
        print(content)
        try:
            # Find JSON in the content
            start_index = content.find('{')
            end_index = content.rfind('}') + 1
            
            if start_index == -1 or end_index == 0:
                raise ValueError("No JSON found in the response")
                
            json_content = content[start_index:end_index]
            result = json.loads(json_content)
            
            return {
                "key": ticket.get("key", "Unknown"),
                "summary": result.get("summary", "No summary available"),
                "linked_issues": result.get("linked_issues", [])
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing OpenAI response for ticket {ticket.get('key', 'Unknown')}: {e}")
            print(f"Response: {content}")
            return {
                "key": ticket.get("key", "Unknown"),
                "summary": "Error parsing response",
                "linked_issues": []
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API for ticket {ticket.get('key', 'Unknown')}: {e}")
        return {
            "key": ticket.get("key", "Unknown"),
            "summary": f"Error: {str(e)}",
            "linked_issues": []
        }

def main():
    """Main function to process all tickets."""
    
    # File paths
    input_file = "jira-beninteg-data-dump.json"
    output_file = "jira-summary.json"
    
    # Read Jira data
    print(f"Reading Jira data from {input_file}...")
    tickets = read_jira_data(input_file)
    print(f"Found {len(tickets)} tickets")
    
    # Process tickets
    results = {}
    for i, ticket in enumerate(tickets):
        ticket_key = ticket.get("key", f"Unknown-{i}")
        print(f"Processing {i+1}/{len(tickets)}: {ticket_key}")
        
        result = process_ticket_with_openai(ticket)
        
        # Only include linked_issues if non-empty
        result_dict = {
            "key": ticket_key,
            "summary": result["summary"]
        }
        
        if result["linked_issues"]:
            result_dict["linked_issues"] = result["linked_issues"]
            
        results[ticket_key] = result_dict
        
        # Write intermediate results to file after every 20 tickets
        if (i + 1) % 20 == 0:
            try:
                print(f"Writing intermediate results to {output_file} after processing {i+1} tickets...")
                with open(output_file, 'w', encoding='utf-8') as file:
                    json.dump(results, file, indent=2)
                print(f"Successfully wrote intermediate results to {output_file}")
            except Exception as e:
                print(f"Error writing intermediate results to output file: {e}")
        
        # Add some delay to avoid rate limits
        if i < len(tickets) - 1:
            time.sleep(1)
    
    # Write final results to file
    try:
        print(f"Writing final results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2)
        print(f"Successfully wrote final results to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    # main()
    print(get_system_prompt())