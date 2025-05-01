
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
from langgraph.prebuilt import   create_react_agent
from langchain_core.tools import tool
from dotenv import load_dotenv
from supervisor_agent import supervisor_agent
from disaster_readiness import readiness_planner_agent
from image_analyzer import analyze_disaster_image
from Navigation import live_disaster_context
from Emergency_response import first_response_agent
from take_input import prepare_inputs
from dotenv import load_dotenv
import operator
from langchain_core.runnables import RunnableLambda
from typing import Dict, Any, Optional, Annotated


load_dotenv()

readiness_agent_runnable = RunnableLambda(
    lambda state: {
        "readiness_result": readiness_planner_agent(
            state.state,
            state.county_name,
            state.personal_profile,
        )
    }
)

first_response_agent_runnable = RunnableLambda(
    lambda state: {
        "first_response_result": first_response_agent(
            state.state,
            state.county_name,
            state.lat,
            state.lon,
            state.personal_profile
        )
    }
)

navigation_agent_runnable = RunnableLambda(
    lambda state: {
        "navigation_result": live_disaster_context(
            state.lat,
            state.lon,
        )
    }
)


visual_agent_runnable = RunnableLambda(
    lambda state: {
        "visual_result": analyze_disaster_image(
            state.image_bytes
        )
    }
)

supervisor_runnable = RunnableLambda(
    lambda state: supervisor_agent(state)
)

prepare_inputs_runnable = RunnableLambda(lambda state: prepare_inputs(state))




class DisasterState(BaseModel):
    user_query: str = None
    lat: float = None
    lon: float = None
    state: str = None
    county: str = None
    county_name: str = None
    personal_profile: Dict[str, Any] = None
    image_bytes: Optional[bytes] = None

    #These will be updated by different agents in parallel
    readiness_result: Dict[str, Any] = None
    first_response_result: Dict[str, Any] = None
    navigation_result: Dict[str, Any] = None
    visual_result: Dict[str, Any] = None
    supervisor_summary: Dict[str, Any] = None


graph = StateGraph(state_schema=DisasterState)


graph.add_node("prepare_inputs_agent", prepare_inputs_runnable)
graph.add_node("supervisor_agent", supervisor_runnable)
graph.add_node("readiness_agent", readiness_agent_runnable)
graph.add_node("first_response_agent", first_response_agent_runnable)
graph.add_node("navigation_agent", navigation_agent_runnable)
graph.add_node("visual_agent", visual_agent_runnable)

graph.add_edge(START, "prepare_inputs_agent")

# 3. Fan out from prepare_inputs
graph.add_edge("prepare_inputs_agent", "readiness_agent")
graph.add_edge("prepare_inputs_agent", "first_response_agent")
graph.add_edge("prepare_inputs_agent", "navigation_agent")
graph.add_edge("prepare_inputs_agent", "visual_agent")

# 4. Each of the agents goes into the supervisor
graph.add_edge("readiness_agent", "supervisor_agent")
graph.add_edge("first_response_agent", "supervisor_agent")
graph.add_edge("navigation_agent", "supervisor_agent")
graph.add_edge("visual_agent", "supervisor_agent")

graph.add_edge("supervisor_agent", END)


compiled_graph = graph.compile()

initial_state = {
    "lat": 37.7749,                     # San Francisco, CA
    "lon": -122.4194,
    "user_query": "There is smoke all around, and I can't see clearly. What should I do?",
    "personal_profile": {
        "age": 72,
        "has_asthma": True,
        "can_walk_long": False,
        "house_type": "Single-story house",
        "dependents": ["grandchild", "spouse"],
        "medical_dependencies": ["oxygen concentrator"],
        "exit_difficulty": "High",
        "communication_access": "Low",
        "power_dependency": "CPAP machine"
    },
    "image_bytes": None   # Optional: could be a base64-encoded image or raw bytes from an upload
}

if __name__ == "__main__":
    result = compiled_graph.invoke(initial_state)
    print(result)
