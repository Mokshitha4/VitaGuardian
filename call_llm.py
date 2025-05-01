import uuid
import time
import asyncio
from typing import Annotated, Sequence
from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_experimental.tools import PythonREPLTool
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import Literal
import functools
import operator
from typing_extensions import TypedDict
import os
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()


api_version = os.getenv('AZURE_OPENAI_API_VERSION')
api_base = os.getenv('AZURE_OPENAI_API_BASE')
api_key = os.getenv('AZURE_OPENAI_KEY')

client = AzureOpenAI(
    api_key = api_key ,
    base_url=f"{api_base}/openai/deployments/gpt-4o-mini",  # Include deployment path,
    api_version=api_version
)


def call_gpt_chat(messages: list, model: str = "gpt-4o-mini", temperature: float = 0.5) -> str:

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content.strip()


# Example usage:
# messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Hello, can you explain about disasters?"}
#     ]

# temperature=0.5,
# print(call_gpt_chat( messages=messages))