import os
import dotenv
from openai import OpenAI
from resolver_prompt import get_resolver_system_prompt, get_resolver_user_prompt
from query_markdown import get_similar_markdown_docs




def main():
    new_ticket_details = input("Enter the details of the ticket troubling you:")
    other_docs = get_similar_markdown_docs(new_ticket_details)
    print("--------------------------------")
    print(other_docs)
    print("--------------------------------")
    user_resolver_prompt = get_resolver_user_prompt(other_docs, new_ticket_details)
    system_resolver_prompt = get_resolver_system_prompt()

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