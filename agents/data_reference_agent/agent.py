from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain.agents.format_scratchpad.log_to_messages import format_log_to_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from typing import List, Dict
from langchain_core.utils.function_calling import convert_to_openai_tool
import json

from agents.data_reference_agent.prompt import SYSTEM_PROMPT


class JiraTicketAgent:
    def __init__(self, tools: List[BaseTool], llm: ChatOpenAI):
        self.tools = tools
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self):
        """Creates the LangChain agent using the OpenAI tools agent."""
        prompt = ChatPromptTemplate.from_messages(  
            [
                (
                    "system",
                    SYSTEM_PROMPT,
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        converted_tools = [convert_to_openai_tool(t) for t in self.tools]

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | self.llm.bind(tools=converted_tools)
            | OpenAIToolsAgentOutputParser()
        )
        return agent


    def analyze_ticket(self, jira_ticket_description: str) -> Dict:
        agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        result = agent_executor.invoke({"input": jira_ticket_description})
        try:
            return result["output"]
            # return json.loads(result["output"])
        except json.JSONDecodeError:
            print(f"Error parsing agent output: {result['output']}")
            return {"data_models": []}
