import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from agents.data_reference_agent.agent import JiraTicketAgent
from agents.data_reference_agent.models import GetDataModelsInput
from agents.data_reference_agent.tools import DataModelExtractionTool


def main():

    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    repo_path = "/Users/jatinsh/Desktop/GitHub/oncall-copilot/confluence-docs-pdfs"



    llm = ChatOpenAI(model="gpt-4-turbo", api_key=openai_api_key)
    embedding_model = OpenAIEmbeddings(api_key=openai_api_key)
    loader = DirectoryLoader(repo_path, recursive=True)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
    chunks = text_splitter.split_documents(documents)

    # print(f"Loaded {len(documents)} documents and split into {len(chunks)} chunks")
    print(chunks[0])

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="chroma-confluence-pdf-docs",
        collection_name="confluence-pdf-docs"
    )

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    data_model_tool = DataModelExtractionTool(llm=llm, retriever=retriever, args_schema=GetDataModelsInput)  
    tools = [data_model_tool]

    jira_ticket_description = """
    The employee enrollment event was not triggered for an employee. Please help debug this issue."""

    agent = JiraTicketAgent(tools=tools, llm=llm)
    result = agent.analyze_ticket(jira_ticket_description)
    print("\nExtracted Data Models:")
    print(result)




if __name__ == "__main__":
    main()