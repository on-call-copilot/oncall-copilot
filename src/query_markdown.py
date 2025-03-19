import os
import dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def doc_to_text(doc: Document) -> str:
    return f"{doc.page_content}\n\n# Document Link: {doc.metadata['page_url']}\n\n"

def get_similar_markdown_docs(jira_ticket_description: str, k: int = 20):
    dotenv.load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    vectorstore = Chroma(
        collection_name="markdown_collection",
        embedding_function=OpenAIEmbeddings(api_key=openai_api_key),
        persist_directory="chroma-confluence-doc-markdowns",
        create_collection_if_not_exists=False
    )

    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": 90})

    docs = retriever.get_relevant_documents(jira_ticket_description)

    docs_str = "\n\n".join([doc_to_text(doc) for doc in docs])

    return docs_str


def main():
    jira_ticket_description = "Tell me everything about the Stedi in-house EDI onboarding process"
    docs = get_similar_markdown_docs(jira_ticket_description)
    print(docs)


if __name__ == "__main__":
    main()