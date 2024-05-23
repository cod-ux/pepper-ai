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

#session = px.launch_app()
#LangChainInstrumentor().instrument()



# Define state

class GraphState(TypedDict):
    request: str
    source_path: str

    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    
    error: str
    messages: List
    generation: str
    code_iteration: int

    response: str




# Define Planner utils

class Plan(BaseModel):
    steps: List[str] = Field(
        description="different steps to follow should be in sorted order"
        )

planner_prompt = ChatPromptTemplate.from_template("""{template}""")

planner = create_structured_output_runnable(Plan, ChatOpenAI(model="gpt-4o", temperature=0, streaming=True), planner_prompt)



# Define code gen utils

class code(BaseModel):

    prefix: str = Field(description="Description of the problem and the approach being taken to solve it")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")
    #description = "Schema for code solutions to execute user requests by writing openpyxl code"


# Graph Nodes


async def plan_steps(state):
    print("\nPlanning step begins...\n")
    plan = planner.invoke({"template": plan_agent_template(state["request"], state["source_path"])})
    print("Planning step: ")
    
    return {"plan": plan.steps}

async def generate_code(state: GraphState):
    request = state["request"]
    messages = state["messages"]
    error = state["error"]
    iterations = state["iterations"]

    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    code_temp = code_gen_template(request)
    code_gen_chain = code_temp | llm.with_structured_output(code)

    code_solution = code_gen_chain.invoke({"messages": messages})
    messages += [
        (
            'assistant',
            f"Code Prefix: {code_solution.prefix} \n\n Imports: {code_solution.imports} \n\n Code block: {code_solution.code}"
        )
    ]

    iterations += 1

    return {"messages": messages, "iterations": iterations, "generation": code_solution}


async def exec_code(state: GraphState):
    pass

async def replan_step(state: GraphState):
    pass

async def should_end(state: GraphState):
    return END



async def reflect(state: GraphState):
    pass


# Create Graph

workflow = StateGraph(GraphState)

workflow.add_node("Planner", plan_steps)
#workflow.add_node("Should end", should_end)

workflow.set_entry_point("Planner")
#workflow.add_edge("Planner", "Should end")

#app = workflow.compile()

config = {"recursion limit": 5}
inputs = {"request": "Add a new sheet called Sheet2", "source": "pivot.xlsx"}

"""async def main():
  for event in app.astream(inputs, config):
    for k, v in event:
        if k != "__end__":
            print(v)
"""
#asyncio.run(main())

state = {"request": "Add a new sheet called Sheet2", "source": "pivot.xlsx"}

response = plan_steps(state)
print(response)

# Next steps
# 1. Change Plan steps to determine split into multiple steps based on complexity of user request
# 2. Iterate and execute through each steps, along with handling erros