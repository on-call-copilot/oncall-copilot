import os
import dotenv
from openai import OpenAI
from resolver_prompt import get_resolver_system_prompt, get_resolver_user_prompt
from query_markdown import get_similar_markdown_docs
from test_similar_tickets import get_similar_tickets



def main():
    new_ticket_details = input("Enter the details of the ticket troubling you:")
    other_docs = get_similar_markdown_docs(new_ticket_details, 3)
    similar_ticket_details = get_similar_tickets(new_ticket_details, similarity_threshold = 0.6)
    ticket_string = ""
    for ticket in similar_ticket_details:
        ticket_string += f"Ticket Key: {ticket['key']}\n Issue: {ticket['issue']}\n Summary: {ticket['issue_summary']}\n RCA: {ticket['rca']}\n Steps: {ticket['steps_taken']}\n Data Models Used: {ticket['data_models']}\n\n"
    user_resolver_prompt = get_resolver_user_prompt(other_docs, new_ticket_details, ticket_string)
    system_resolver_prompt = get_resolver_system_prompt()

    print(user_resolver_prompt)
    dotenv.load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_resolver_prompt},
            {"role": "user", "content": user_resolver_prompt},
        ],
    )
    print(response.choices[0].message.content)



if __name__ == "__main__":
    main()