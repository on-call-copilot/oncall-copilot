import os
from typing import Optional
import dotenv
from openai import OpenAI
from resolver_prompt import get_resolver_system_prompt, get_resolver_user_prompt
from query_markdown import get_similar_markdown_docs
from jira_integration import JiraIntegrator
from test_similar_tickets import get_similar_tickets
from utils.files import read_markdown_file

jira_client = JiraIntegrator()
def triage_ticket(new_ticket_details: Optional[str] = None, ticket_url: str = None):
    # new_ticket_details = input("Enter the details of the ticket troubling you:")
    if new_ticket_details is None:
        new_ticket_details = read_markdown_file("input.txt")
    other_docs = get_similar_markdown_docs(new_ticket_details, 3)
    similar_ticket_details = get_similar_tickets(new_ticket_details, similarity_threshold = 0.6)
    ticket_string = ""
    for ticket in similar_ticket_details:
        ticket_string += f"Ticket Key: {ticket['key']}\n Issue: {ticket['issue']}\n Summary: {ticket['issue_summary']}\n RCA: {ticket['rca']}\n Steps: {ticket['steps_taken']}\n Data Models Used: {ticket['data_models']}\n\n"
    user_resolver_prompt = get_resolver_user_prompt(other_docs, new_ticket_details, ticket_string)
    system_resolver_prompt = get_resolver_system_prompt()

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
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    jira_client.post_jira_comment(ticket_url=ticket_url, comment_text=response.choices[0].message.content)
    next_step = False
    while next_step:
        user_input = input("\n\ngive next prompt file name(leave empty to end chat)")
        if user_input == "":
            next_step = False
        else:
            file_content = read_markdown_file(user_input)

            print(file_content)
            
            messages.append({"role": "user", "content": file_content})
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
            )
            print("\n\n\n")
            print(print(response.choices[0].message.content))
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            print("\n\n\n")
            jira_client.post_jira_comment(ticket_url=ticket_url, comment_text=response.choices[0].message.content)
if __name__ == "__main__":
    triage_ticket()