import os
import toml
import asyncio
import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor

from langchain_openai import ChatOpenAI

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import TypedDict, List, Tuple, Annotated
import operator

from langchain.chains.openai_functions import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, END

from agent_templates import plan_agent_template, code_gen_template



# setup

secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"
github_secrets = "secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = toml.load(secrets)["TAVILY_API_KEY"]

session = px.launch_app()
LangChainInstrumentor().instrument()



# Define state

class GraphState(TypedDict):
    input: str
    source_path: str

    plan: str
    
    error: str
    messages: List
    generation: str
    code_iteration: int

    response: str




# Define Planner utils

class Plan(BaseModel):
    steps: str = Field(
        description="different steps to follow should be in sorted order"
        )

planner_prompt = ChatPromptTemplate.from_template("""{template}""")

planner = create_structured_output_runnable(Plan, ChatOpenAI(model="gpt-4o", temperature=0, streaming=True), planner_prompt)



# Define code gen utils

class code(BaseModel):

    prefix: str = Field(description="Description of the problem and the approach being taken to solve it")
    imports: str = Field(description="Code block import statements")
    code_block: str = Field(description="Code block not including import statements")
    #description = "Schema for code solutions to execute user requests by writing openpyxl code"



llm = ChatOpenAI(temperature=0, model="gpt-4o")
code_temp = code_gen_template()
code_gen_chain = code_temp | llm.with_structured_output(code)



# Graph Nodes

def plan_step(state):
    print("\nPlanning step begins...\n")
    plan = planner.invoke({"template": plan_agent_template(state["input"], state["source_path"])})
    print("Planning step: ")
    

    return {"plan": plan.steps}

def generate_code(state):
    request = state["input"]

def check_code(state):
    pass

def reflect(state):
    pass

def replan_step(state):
    pass


# Compile Graph


