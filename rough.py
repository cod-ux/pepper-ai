import os
import toml
import asyncio
import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_agent_executor

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import TypedDict, List, Tuple, Annotated
import operator

from langchain.chains.openai_functions import create_structured_output_runnable, create_openai_fn_runnable
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agent_templates import plan_agent_template

# setup

secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"
github_secrets = "secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = toml.load(secrets)["TAVILY_API_KEY"]

session = px.launch_app()
LangChainInstrumentor().instrument()


print("....Finished setting up")

# Define state

class GraphState(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    source_path: str
    response: str


# Define Planner utilities

class Plan(BaseModel):
    steps: List[str] = Field(
        description="different steps to follow should be in sorted order"
        )

planner_prompt = ChatPromptTemplate.from_template("""{template}""")

planner = create_structured_output_runnable(Plan, ChatOpenAI(model="gpt-4o", temperature=0, streaming=True), planner_prompt)

def plan_step(state):
    print("\nPlanning step begins...\n")
    plan = planner.invoke({"template": plan_agent_template(state["input"], state["source_path"])})
    print("Planning step: ")
    return {"plan": plan.steps}

def generate_code(state):
    pass

def check_code(state):
    pass

def reflect(state):
    pass

def replan_step(state):
    pass

state = {
    "input": "How many empty spaces are there in each excel sheet?", 
    "source_path": "/Users/suryaganesan/vscode/ml/projects/reporter/pivot.xlsx"
}

response = plan_step(state=state)
print(response)