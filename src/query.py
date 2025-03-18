import os
import dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompt_template import ON_CALL_COP_PROMPT, create_prompt_for_confluence
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


def main():
    dotenv.load_dotenv()
    persist_directory = "chroma-db"  # adjust if needed

    # Load the existing Chroma store
    vectorstore = Chroma(
        collection_name="confluence-docs",  
        embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
        persist_directory=persist_directory
    )

    user_query = input("Enter your prompt: ")
    # query = "Find where the employee hr data file is being created for selerix and suggest improvements in the code"
    docs = vectorstore.similarity_search(user_query, k=10)

    seen = set()
    unique_docs = []
    for doc in docs:
        content_hash = hash(doc.page_content)
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)

    if not unique_docs:
        print("No documents found.")
        exit()

    #Convert unique_docs to a string
    unique_docs_str = "\n".join([doc.page_content for doc in unique_docs])

    prompt = ChatPromptTemplate.from_messages(
         [
            (
                "system",
                ON_CALL_COP_PROMPT,
            ),
            ("user", create_prompt_for_confluence(user_query, unique_docs_str)),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

    print(prompt)

    breakpoint()

    response = llm.invoke(prompt.format(agent_scratchpad=[],  Decagon=""))

    print(response)

    return response
    print("\n=== OpenAI's Answer ===")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
