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

You are also an expert at analyzing Jira tickets and extracting key information. 

The Jira tickets follow this JSON format:
{jira_ticket_format}

Pay special attention to the description, comments, and RCA fields as they often contain the most relevant information about the issue.

Analyze the Jira ticket given by user, read all the content, description, comments, etc. and understand the issue user was facing and the detailed reason 
due to which the issue occurred and steps taken to resolve it:
    1. issue: A concise summary of the issue being faced(problem faced in ticket and blockers happening due to it, don't include the reason found during investigation on what caused it)
    2. issue_summary: A concise summary of the issue(summary of problem problem faced in ticket and top level reason due to which the issue occurred don't include the solution)
    3. rca: A detailed summary of the reason found during investigation on what caused the issue
    4. steps_taken: summary of steps taken to resolve the issue. include code snippets used to debug and fix they are available in the data. use markdown for code snippets.
    5. Data Models: A list of data models names used to debug and fix the issue. this would be mostly available in code snippets.
    Output only the json object as string and not in markdown format.
    Format your response exactly as follows:
    {{
        "issue": "Issue being faced in ticket", 
        "issue_summary": "Your summary of the ticket issue here",
        "rca": "A detailed summary of the reason found during investigation on what caused the issue",
        "steps_taken": "summary of steps taken to resolve the issue.",
        "data_models": "A list of data models names used to debug and fix the issue.ex: [InsuranceCompanyCarrierLineInfo, CompanyInsuranceInfo]"
    }}
    
    If no linked issues are found, return an empty list.
"""

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def write_openai_response_to_file(ticket_key: str, content: str, output_file: str):
    """
    Write OpenAI response content to a file with the specified format.
    
    Args:
        ticket_key (str): The Jira ticket key
        content (str): The raw content from OpenAI
        output_file (str): The file to write to
    """
    try:
        with open(output_file, 'a', encoding='utf-8') as file:
            file.write(f"KEY: {ticket_key}\n")
            file.write(f"{content}\n\n\n")
        print(f"Successfully wrote OpenAI response for {ticket_key} to {output_file}")
    except Exception as e:
        print(f"Error writing OpenAI response to file: {e}")

def process_ticket_with_openai(ticket: Dict[str, Any], failed_tickets: List[str], responses_file: str) -> Dict[str, Any]:
    """Process a ticket with OpenAI to get summary and linked issues."""
    prompt = create_prompt_for_ticket(ticket)
    ticket_key = ticket.get("key", "Unknown")
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # You can adjust the model as needed
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content.strip()
        print(f"Processing ticket {ticket_key}")
        print(content) # Print part of the raw response for debugging
        
        # Write the raw response to the file
        write_openai_response_to_file(ticket_key, content, responses_file)
        
        try:
            # Find JSON in the content
            # start_index = content.find('{')
            # end_index = content.rfind('}') + 1
            # if start_index == -1 or end_index == 0:
            #     print(f"WARNING: No JSON found in the response for ticket {ticket_key}")
            #     raise ValueError("No JSON found in the response")
                            
            result = json.loads(content)
            print(f"Successfully parsed JSON for ticket {ticket_key}")
            
            return {
                "key": ticket_key,
                "issue": result.get("issue", "No issue available"),
                "issue_summary": result.get("issue_summary", "No issue summary available"),
                "rca": result.get("rca", "No RCA available"),
                "steps_taken": result.get("steps_taken", "No steps taken information available"),
                "data_models": result.get("data_models", "No data models information available")
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing OpenAI response for ticket {ticket_key}: {e}")
            print(f"Response: {content}")
            failed_tickets.append(ticket_key)
            return {
                "key": ticket_key,
                "issue": "Error parsing response",
                "issue_summary": "Error parsing response",
                "rca": "Error parsing response",
                "steps_taken": "Error parsing response",
                "data_models": "Error parsing response"
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API for ticket {ticket_key}: {e}")
        failed_tickets.append(ticket_key)
        return {
            "key": ticket_key,
            "issue": f"Error: {str(e)}",
            "issue_summary": f"Error: {str(e)}",
            "rca": f"Error: {str(e)}",
            "steps_taken": f"Error: {str(e)}",
            "data_models": f"Error: {str(e)}"
        }

def main():
    """Main function to process all tickets."""
    
    # File paths
    input_file = "jira-exports/jira-beninteg-data-dump.json"
    output_file = "outputs/jira-summary_v2_4o.json"
    responses_file = "outputs/openai-responses-jira.txt"
    
    # Initialize the failed_tickets list
    failed_tickets = []
    
    # Clear the responses file if it exists
    try:
        with open(responses_file, 'w', encoding='utf-8') as file:
            file.write("# OpenAI Responses for Jira Tickets\n\n")
    except Exception as e:
        print(f"Error initializing responses file: {e}")
    
    # Read Jira data
    print(f"Reading Jira data from {input_file}...")
    tickets = read_jira_data(input_file)
    print(f"Found {len(tickets)} tickets")
    
    # Process tickets
    results = {}
    for i, ticket in enumerate(tickets):
        ticket_key = ticket.get("key", f"Unknown-{i}")
        print(f"Processing {i+1}/{len(tickets)}: {ticket_key}")
        
        result = process_ticket_with_openai(ticket, failed_tickets, responses_file)
        
        # Add result to results dictionary
        results[ticket_key] = {
            "key": ticket_key,
            "issue": result["issue"],
            "issue_summary": result["issue_summary"],
            "rca": result["rca"],
            "steps_taken": result["steps_taken"],
            "data_models": result["data_models"]
        }
        
        # Write intermediate results to file after every 20 tickets
        if (i + 1) % 20 == 0:
            try:
                print(f"Writing intermediate results to {output_file} after processing {i+1} tickets...")
                with open(output_file, 'w', encoding='utf-8') as file:
                    json.dump(results, file, indent=2)
                print(f"Successfully wrote intermediate results to {output_file}")
            except Exception as e:
                print(f"Error writing intermediate results to output file: {e}")
            
            time.sleep(2)
        
        
    
    # Print list of keys that had issues
    if failed_tickets:
        print("\nThe following tickets had issues during analysis:")
        for key in failed_tickets:
            print(f"- {key}")
        
        # Also write failed tickets to a file
        try:
            with open("outputs/failed_tickets.txt", 'w', encoding='utf-8') as file:
                file.write("# Failed Tickets\n\n")
                for key in failed_tickets:
                    file.write(f"{key}\n")
            print("List of failed tickets written to failed_tickets.txt")
        except Exception as e:
            print(f"Error writing failed tickets to file: {e}")
    else:
        print("\nAll tickets were processed successfully!")
    
    # Write final results to file
    try:
        print(f"Writing final results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2)
        print(f"Successfully wrote final results to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()