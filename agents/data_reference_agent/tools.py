import json
from langchain_community.vectorstores import Chroma
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.data_reference_agent.models import GetDataModelsInput
from langchain_core.vectorstores import VectorStoreRetriever


class DataModelExtractionTool(BaseTool):
    name : str = "data_model_extractor"
    description : str = (
        "Identifies and extracts relevant data models and their fields."
    )
    args_schema: type[BaseModel] = GetDataModelsInput
    retriever: VectorStoreRetriever = Field(default=None,exclude=True)
    llm: ChatOpenAI 

    def __init__(self, retriever: VectorStoreRetriever, llm: ChatOpenAI, **kwargs):
        super().__init__(llm=llm, retriever=retriever, **kwargs)


    def _run(self, ticket_description: str) -> str:
        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(ticket_description)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Use retrieval prompt to improve context (optional, but good practice)
        retrieval_prompt_template = """
        You are an expert in analyzing JIRA tickets for the "Benefits Marketplace Integrations" team.
        Given the JIRA ticket description and the provided context from Confluence documentation,
        rephrase the ticket description to include any relevant details from the context.
        Do NOT attempt to list specific data models or fields. Focus on providing a comprehensive description.

        Context:
        {context}
        """
        retrieval_prompt = ChatPromptTemplate.from_template(retrieval_prompt_template)
        retrieval_chain = retrieval_prompt | self.llm | StrOutputParser()
        contextualized_ticket_desc = retrieval_chain.invoke({"context": context})

        print(f"Context!!!: {contextualized_ticket_desc}")
        print("------------------CONTEXT ENDSSSS---------------------")

        # Extract data models (using the improved context)
        extraction_prompt_template = """
        You are an expert in analyzing JIRA tickets for the "Benefits Marketplace Integrations" team.
        Based on the JIRA ticket description and Confluence context, identify the data models and their fields.
        Return it as a json:

        {{
            "data_models": [
                {{
                    "model": "DataModelName1",
                    "fields": ["field1", "field2", "field3"]
                }},
                {{
                    "model": "DataModelName2",
                    "fields": ["fieldA", "fieldB"]
                }}
            ]
        }}
        If no relevant information, return: `{{"data_models": []}}`

        JIRA Ticket Description:
        {ticket_description}

        Context:
        {context}
        """
        extraction_prompt = ChatPromptTemplate.from_template(extraction_prompt_template)
        extraction_chain = extraction_prompt | self.llm | StrOutputParser()
        result = extraction_chain.invoke({"ticket_description": ticket_description, "context": contextualized_ticket_desc})

        # print(f"Result!!!: {json.dumps(result)}")

        return result

        # try:
        #     return json.loads(result)
        #     # return json.dumps(json.loads(result))
        # except json.JSONDecodeError:
        #     print(f"Error: Could not parse LLM output as JSON: {result}")
        #     return json.dumps({"data_models": []})
    
    def _arun(self, ticket_description: str):
        raise NotImplementedError("This tool does not support async")
