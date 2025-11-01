import os
from langchain_tavily import TavilySearch
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

tavily_search_tool = TavilySearch(
    max_results=1,
    topic="general",
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"), # or your deployment
    api_version="2024-07-01-preview", # or your api version
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Setup Langchain agent with both tools
tools = [tavily_search_tool]
agent = create_react_agent(
    model=llm,
    tools=tools,
)

def callTavilySearch(prompt_message_list):
    response = agent.invoke({"messages": prompt_message_list})
    return response["messages"][-1].content