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

from temp_manipulate import planner_template, format_request, format_code_request, code_chain_template, retrieve_context


# setup

secrets = "/Users/suryaganesan/Documents/GitHub/reporter/secrets.toml"
github_secrets = "secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = toml.load(secrets)["TAVILY_API_KEY"]

session = px.launch_app()
LangChainInstrumentor().instrument()

llm = ChatOpenAI(temperature=0, model="gpt-4o")

# Define state

class GraphState(TypedDict):
    request: str
    source_path: str

    tasks: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    
    error: str
    messages: List
    generation: str
    code_iteration: int

    response: str

class Plan(BaseModel):
    tasks: List[str] = Field(
        description="different steps to follow should be in sorted order"
        )

class code(BaseModel):
    prefix: str = Field("Description of the problem and the approach being taken in the solution")
    imports: str = Field("Code block import statements")
    code: str = Field("Code block excluding import statements")
    description = "Schema for code solutions to execute openpyxl related user requests"


prompt = code_chain_template() # Retrieved and added context docs in prompt template
code_chain = prompt | llm.with_structured_output(code)

# Function: Plan task

def plan_steps(state):
    planner_prompt = planner_template()
    planner = create_structured_output_runnable(Plan, ChatOpenAI(model="gpt-4o", temperature=0, streaming=True), planner_prompt)

    print("\nPlanning step begins...\n")

    plan = planner.invoke({"messages": state["messages"]})
    print("Planning step: \n")
    
    return {"plan": plan.tasks}

# Function: Write code


async def generate_code(task, messages):
    context = retrieve_context(task)

    print("Generating code....")
    print("\nMessage being passed to code chain: \n", messages)
    print(f"Message type: {type(messages)}")

    code_object = code_chain.invoke({"messages": messages})

    return code_object

async def check_code(state: GraphState):
    pass

async def should_end(state: GraphState):
    pass

# Preparing query for planning
request = "Find a unique column that can be used as an ID commonly between both the sheets in the excel and copy the column to a new excel sheet." 

g_state = {}
g_state["request"] = request
g_state["imports"] = ''
g_state["code_block"] = ''
g_state["executed_tasks"] = ''
st_state = {"source_path": "/Users/suryaganesan/Documents/GitHub/reporter/excel_source/sales_data_sample.xlsx"}


g_state["source_path"] = st_state["source_path"]
formatted_request = format_request(request, g_state["source_path"]) 

g_state["messages"] = [('user', formatted_request)] # Updating source path and adding user request

# Executing Graph for making plan

tasks = plan_steps(g_state)

print(tasks['plan'])

tasks_string = 'Plan to be followed: \n' + '\n'.join(tasks["plan"])
messages = g_state["messages"]
g_state["tasks"] = tasks["plan"]

messages += [('system', tasks_string)]
g_state["messages"] = messages

print(f"\nMessages list: \n{messages}")

print("\nPreparing tasks to be executed...")



for count, task in enumerate(list(g_state["tasks"])):
    #messages += ('system', f"Last extracted task to be executed: {task}")
    #g_state["messages"] = messages
    print("\nFormatting code request\n")
    code_request = format_code_request(task_to_be_executed=task)
    messages = g_state["messages"]

    messages += [('user', f' Next task to be executed: {task}')]
    g_state["messages"] = messages
    messages = g_state["messages"]

    print("Message being passed from for loop: \n", messages)

    code = generate_code(task=task, messages=messages)

    print(f"\nTask {count}: {task}\n")
    print(f"\nCode prefix: \n {code.prefix}\n")
    print(f"\nCode imports: \n {code.imports}\n")
    print(f"\nCode Block: \n {code.code}\n")

    g_state["imports"] = code.imports
    g_state["code_block"] = code.code
    g_state["executed_tasks"] += f"\nTask {count}: {task}\n"
    executed_tasks = g_state["executed_tasks"]
    print("Executed tasks: " + executed_tasks)

    messages += [("system", f"The last added step to the code was: {task}. \nThe Code solution so far is: {code.imports} \n {code.code}")]
    messages += [('system', f"So far the code written will be able to complete the following tasks from the plan: \n{executed_tasks}")]
    g_state["messages"] = messages

    print(f"\nMessages so far looks like: \n {messages}\n")


print("Loop over.\n")
print(f"Here is the code solution: \nCode imports:\n{code.imports}\nCode block:\n{code.code}")

x = input("Should execution be initiated? ")

# Check execution

try:
    exec(code.imports)

except Exception as e:
    g_state["error"] = e
    g_state["messages"] += f"Error with import statement: \n{e}"

    print(f"Error with import statement: {e}")

try:
    exec(code.code)

except Exception as e:
    g_state["error"] = e
    g_state["messages"] += f"Error with code block statement: \n{e}"

    print("Error with code block")

print("\n Code successfully executed.\n")

end_in = input("Quit?...")

