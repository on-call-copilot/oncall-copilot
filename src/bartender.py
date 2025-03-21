import json
import os
from typing import Optional
import dotenv
from openai import OpenAI
from resolver_prompt import get_resolver_system_prompt, get_resolver_user_prompt, get_followup_resolver_system_prompt
from query_markdown import get_similar_markdown_docs
from jira_integration import JiraIntegrator
from test_similar_tickets import get_similar_tickets
from utils.files import read_markdown_file
from follow_up_prompt import FOLLOW_UP_PROMPT
from rippling_api import RipplingApiHandler

jira_client = JiraIntegrator()
def triage_ticket(new_ticket_details: Optional[str] = None, ticket_url: str = None):
    if new_ticket_details is None:
        new_ticket_details = read_markdown_file("input.txt")
    other_docs = get_similar_markdown_docs(new_ticket_details, 3)
    similar_ticket_details = get_similar_tickets(new_ticket_details, similarity_threshold = 0.6)
    ticket_string = ""
    for ticket in similar_ticket_details:
        ticket_string += f"Ticket Key: {ticket['key']}\n Issue: {ticket['issue']}\n Summary: {ticket['issue_summary']}\n RCA: {ticket['rca']}\n Steps: {ticket['steps_taken']}\n Data Models Used: {ticket['data_models']}\n\n"
    user_resolver_prompt = get_resolver_user_prompt(other_docs, new_ticket_details, ticket_string)
    system_resolver_prompt = get_resolver_system_prompt()

    # Initialize the RipplingApiHandler
    rippling_handler = RipplingApiHandler()

    response_to_post_on_jira = None

    dotenv.load_dotenv()
    messages = [
            {"role": "system", "content": system_resolver_prompt},
            {"role": "user", "content": user_resolver_prompt},
        ]
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
    )
    print(response.choices[0].message.content)

    response_to_post_on_jira = response.choices[0].message.content

    
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    messages.append({"role": "user", "content": FOLLOW_UP_PROMPT})
    
    follow_up_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
    )
    print("\nFollow-up response:")
    print(follow_up_response.choices[0].message.content)
    
    try:
        data_models_response = json.loads(follow_up_response.choices[0].message.content)
        company_id = data_models_response.get("company_id")
        data_models = data_models_response.get("data_models", [])

        noyo_info = None
        comm_details = None

        if "NoyoCompanyPlanInfo" in data_models:
            print("\nFetching Noyo Company Plan Info:")
            noyo_info = rippling_handler.get_noyo_company_plan_info(company_id)
            print(noyo_info)

        if any("Communication" in model for model in data_models):
            print("\nFetching Custom Communication Details:")
            comm_details = rippling_handler.get_custom_communication_detail(company_id)
            print(comm_details)

        # Only proceed with the additional message if we have either noyo_info or comm_details
        if noyo_info or comm_details:
            additional_context = "Here is additional context from our systems:\n\n"
            if noyo_info:
                additional_context += "Noyo Company Plan Information:\n"
                additional_context += json.dumps(noyo_info, indent=2) + "\n\n"
            if comm_details:
                additional_context += "Custom Communication Details:\n"
                additional_context += json.dumps(comm_details, indent=2)

            messages.append({"role": "user", "content": additional_context})

            # modify the system prompt to include the additional context
            messages[0]["content"] = get_followup_resolver_system_prompt()

            final_response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
            )
            print("\nFinal analysis with additional context:")
            print(final_response.choices[0].message.content)
            response_to_post_on_jira = final_response.choices[0].message.content
    except json.JSONDecodeError:
        print("Failed to parse follow-up response as JSON")

    
    # Enables Jira comment posting
    if ticket_url and response_to_post_on_jira:
        jira_client.post_jira_comment(ticket_url=ticket_url, comment_text=response_to_post_on_jira.choices[0].message.content)
    
if __name__ == "__main__":
    triage_ticket()