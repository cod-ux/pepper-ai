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

from agent_templates import planner_template, format_request, format_code_request, code_gen_template, retrieve_context



# setup

secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"
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


prompt = code_gen_template() # Retrieved and added context docs in prompt template
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


def generate_code(task, messages):
    context = retrieve_context(task)

    print("Generating code....")
    print("\nMessage being passed to code chain: \n", messages)
    print(f"Message type: {type(messages)}")

    code_object = code_chain.invoke({"messages": messages})

    return code_object


# Preparing query for planning
request = "Find a unique column that can be used as an ID commonly between both the sheets in the excel and copy the column to a new excel sheet." 

g_state = {}
g_state["request"] = request
g_state["imports"] = ''
g_state["code_block"] = ''
g_state["executed_tasks"] = ''
st_state = {"source_path": "/Users/suryaganesan/vscode/ml/projects/reporter/sales_data_sample.xlsx"}


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
    code_request = format_code_request(request=g_state["request"], source=g_state["source_path"], task_to_be_executed=task)
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


"""
Exp 1: Add the entire prompt to one message

Result: Did not work, still made a multi-step plan for a simple request

Exp 2: Change the propmt to identify tasks instead of make a plan.

Result: Tasks are more accurate and works.
Challenge: Individual tasks are some time exploratory and provide some answers for the next step to use, 
but since the generated code is dynamically executed, there isn't a way to add the exploration script's response to the messages.

Exp 3: Ask the generated code to always return a response with the same variable name to extract and add to messages if the response is not None.
Implementation: 
1. Planner needs to run on messages not template, and messages variable should be used from state class. (done)
2. Generated code should be asked to: Save file with the same source file_name and return a response variable with the same name.
3. Response needs to be added to messages by checking if there is a response every time code is executed

Challenge in 3-1: planner template encounters some error when loading template from {template function}
Solution: Creating a planner object from llms newly every time planner node is called. Need to check if this is time consuming.

Challenge 3-2: First loop runs well, but adding to the messages seems to pop an error when the second loop starts.
Solution: Needed to create the code gen chain only once and not multiple times

Challenge 3-3: We want the user request to be correctly executed in the final step. To do that we were thinking of
breaking the request to list of tasks, then execute each task individually. Hoping that executing step by step would result in
minimal errors. But this requires viewing the new state of the excel after each step. Instead would be accurate if we just, iteratively
add code adn executing only in the end?
Trial solution: At each task take the code solution so far, mentioning the tasks it achieves and provide a new task to add to the
existing code. And when there is no more tasks left to complete, execute the code.

Rewriting Exp 3: Make the flow such that at each step code is added iteratively to each task and executed at the end when the
list is exhausted.

Implementation: 
1. No change to planner (done)
2. Stop messages from adding sheet views at every step. (done)
3. First message after planning should be include list of tasks. (done)
4. Need to maintain a variable for past_code_steps. (done)
5. After exec each task, add message to say here are the steps coded. (done)
6. Before exec each task, Add here is the task that needs to be added to the code. (done)

7. Ask the code to return a response object with the same variable name in the end, to check if the function was executed successfully or what the error was.
But would that be necessary? What if we just executed and figured what the mistake was ourselves? This would probably help debugging a lot.
But still, I'll have to ask the LLM to include try statements everywhere and ask it to write and return code that is easily debuggable.
But again, I can still ask it to write debuggable code with a lot of try statements, so that the error can be specified.
Preferably for simplicity, we do not include try statements inside and catch adn use the error only when we execute the code.
The alternative would be to ask the LLM return a response object, describing the problem when an expected error is thrown. 
Which will be used for debugging the code better.
We're gonna choose simple and just use the error that may be caught during dynamic execution itself. Cuz the alternative is a lot of work and complexity.
Cancelled step 7.

Solution: Created an iterative coding process where an additional task is completed at each step to produce the final code
that achieves all tasks.

Exp 4: Add a try statement to execute the imports and code blocks. And the functionality to restart the generation process
one additional time to correct the error.

Implementation:
1. Add try statements and returning the error to the state variable error. (done)
2. Add error variable to messages if caught. (done)

Exp 5: Make the Graph to add nodes - plan, generate, check & reflect, replan
"""