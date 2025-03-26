import json
import os
from typing import Optional
import dotenv
from openai import OpenAI
from resolver_prompt import get_resolver_system_prompt, get_resolver_user_prompt, get_followup_resolver_system_prompt
from query_markdown import get_similar_markdown_docs
from jira_integration import JiraIntegrator
from test_similar_tickets import get_similar_tickets
from utils.files import format_json_to_string, read_markdown_file
from follow_up_prompt import FOLLOW_UP_PROMPT
from rippling_api import RipplingApiHandler

def triage_ticket():
   
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
        model="gpt-4o",
        messages=messages,
    )
    with open("response.md", "w") as file:
        file.write(response.choices[0].message.content)
    print(response.choices[0].message.content)

    # response_to_post_on_jira = response.choices[0].message.content

    
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    messages.append({"role": "user", "content": FOLLOW_UP_PROMPT})
    
    follow_up_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print("\nFollow-up response:")
    print(follow_up_response.choices[0].message.content)
    
    try:
        data_models_response = json.loads(follow_up_response.choices[0].message.content)
        company_id = data_models_response.get("company_id")
        company_plan_info_id = data_models_response.get("company_plan_info_id", None)
        data_models = data_models_response.get("data_models", [])

        noyo_info = None
        comm_details = None
        next_data = False
        if "NoyoCompanyPlanInfo" in data_models:
            print("\nFetching Noyo Company Plan Info:")
            noyo_info = rippling_handler.get_noyo_company_plan_info(company_id, company_plan_info_id)
            print(noyo_info)
            next_data = True

        # if any("Communication" in model for model in data_models):
        #     print("\nFetching Custom Communication Details:")
        #     comm_details = rippling_handler.get_custom_communication_detail(company_id)
        #     print(comm_details)
        #     next_data = True
        # breakpoint()
        # Only proceed with the additional message if we have either noyo_info or comm_details
        additional_context = "Here is additional context from our systems. Carefully analyze the data and use it to help resolve the issue:\n\n"
        if next_data:
            if noyo_info:
                additional_context += "Noyo Company Plan Info objects models in database:\n"
                additional_context += format_json_to_string(json.loads(noyo_info))
            if comm_details:
                additional_context += "Custom Communication Details:\n"
                additional_context += format_json_to_string(json.loads(comm_details))
        else:
            continue_chat = input("Please put the required data in the next_input.txt file and enter 'Y' to continue or anything else to end")
            if continue_chat == 'Y' or continue_chat == 'y':
                additional_context += read_markdown_file("next_input.txt")
            else:
                print("Thank you for using the service")
                return
        messages[3]["content"] = additional_context

        # modify the system prompt to include the additional context
        messages[0]["content"] = get_followup_resolver_system_prompt()

        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        print("\nFinal analysis with additional context:")
        print(final_response.choices[0].message.content)
        with open("response.md", "a") as file:
            file.write("\n" * 10)
            file.write("Final Analysis with additional context:\n\n")
            file.write(final_response.choices[0].message.content)
            # response_to_post_on_jira = final_response.choices[0].message.content
    except json.JSONDecodeError:
        print("Failed to parse follow-up response as JSON")

    
    
if __name__ == "__main__":
    triage_ticket()