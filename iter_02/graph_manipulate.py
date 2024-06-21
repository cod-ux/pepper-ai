import os
import toml
import asyncio
import operator
import pandas as pd
import sys
from io import StringIO

from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_functions import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor
from typing import TypedDict, List, Tuple, Annotated
from temp_manipulate import (
    planner_template,
    format_request,
    format_code_request,
    code_chain_template,
    data_analyst_template
)


# OpenAI init.

secrets = "/Users/suryaganesan/Documents/GitHub/reporter/secrets.toml"
github_secrets = "secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# Phoenix init.

session = px.launch_app()
LangChainInstrumentor().instrument()


# Defining class objects for graph

class GraphState(TypedDict):
    request: str # Set
    source_path: str # Set
    past_execs: List

    tasks: List[str]
    past_tasks: List[str]
    current_task: str
    
    error: str
    messages: List
    generation: str
    iterations: int # Set
    max_iterations: int # Set
    reflect: str


    response: str

class Plan(BaseModel):
    tasks: List[str] = Field(
        description="List of tasks to complete to fulfill the user request"
        )

class code(BaseModel):
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block for import statements in the code")
    code: str = Field(description="Code block for the code statement without import statements")
    description: str = "Schema for code solutions to execute openpyxl related user requests"

class answer(BaseModel):
    ans: str = Field("Results of the executed program")

# Preparing code_chain()

code_prompt = code_chain_template()
code_chain = code_prompt | llm.with_structured_output(code)
analyst_prompt = data_analyst_template()
analyst_chain = analyst_prompt | llm.with_structured_output(answer)

# Node functions

def plan_steps(state: GraphState):
    messages = state["messages"]
    past_tasks = state["past_tasks"]
    past_execs = state["past_execs"]
    reflect = state["reflect"]
    error = state["error"]
    past_tasks = []
    reflect = ''

    if error == "yes":
        messages += [("system", f"Now I should try again to recreate a plan that doesn't without producing any errors, if the error was due to the plan. Let's rewrite a new plan if necessary.")]

    if len(past_execs) > 4:
        exec_string = ''
        for execs in past_execs[-4:0]:
            req = execs["question"]
            update = execs["answer"]
            exec_string += f"\nPast Request: {req}\nTable: {update}\n"
        messages += [("system", f"These are the past 4 requests from the user along with a view of how the excel sheet looked like after executing the request: \n{exec_string}")]

    if len(past_execs) < 4:
        exec_string = ''
        for execs in past_execs:
            req = execs["question"]
            update = execs["answer"]
            exec_string += f"\nRequest: {req}\nTable: {update}\n"
        messages += [("system", f"These are the past few requests from the user along with a view of how the excel sheet looked like after executing the request: \n{exec_string}")]


    planner_prompt = planner_template()
    planner = create_structured_output_runnable(Plan, ChatOpenAI(model="gpt-4o", temperature=0, streaming=True), planner_prompt)

    print("\nPlanning step begins...\n")

    plan = planner.invoke({"messages": messages})
    print(f"Planning step: \n, {plan.tasks}")
    plan_string = ''

    for i, task in enumerate(plan):
        plan_string += f'\n Task {i}: {task}'

    print(plan_string)

    messages += [('system', f"For the user request, this is the list of tasks I need to achieve to fulfill the request: \n{plan_string}")]
    
    return {"tasks": plan.tasks, "messages": messages, "past_tasks": past_tasks, "reflect": reflect, "current_task": f"Plan completed..."}

# Function: Write code

def generate_code(state: GraphState):
    messages = state["messages"]
    iterations = state["iterations"]
    error = state["error"]
    generation = state["generation"]
    tasks = state["tasks"]
    past_tasks = state["past_tasks"]

    plan_string = ''

    for i, task in enumerate(tasks):
        plan_string += f'\n Task {i}: {task}'

    print("Generating code....")

    if error == "yes":
        messages += [("system", f"Now I should try again to generate code with the newly written plan that wouldn't produce any errors during execution, in case the error was due to the written code. This is the plan to follow: \n{plan_string}")]

    for count, task in enumerate(tasks):

        print(f"\nCoding: {count}. {task}\n")
        code_request = format_code_request(task_to_be_executed=task)

        messages += [('system', f'{code_request}')]

        generation = code_chain.invoke({"messages": messages})
        past_tasks += [f'{count}. {task}']
        past_tasks_string = ''

        for i, task in enumerate(past_tasks):
            past_tasks_string += f'\n Task {i}: {task}'

        messages += [("system", f"The last added step to the code was: {task}. \nThe Code solution so far is: \n{generation.imports} \n {generation.code}")]
        messages += [('system', f"So far the code written will be able to complete the following tasks from the plan: \n{past_tasks_string}")]

    iterations += 1
    print("Reached end of generation...")

    #last_msgs = messages[-2:]
    #last_indx = -2*len(task)
    #messages = messages[:last_indx] + last_msgs
    return {"generation": generation, "messages": messages, "iterations": iterations, "current_task": "Executing code..."}

def check_code(state: GraphState):
    print("Code is being checked....")
    messages = state["messages"]
    generation = state["generation"]
    error = state["error"]
    iterations = state["iterations"]
    reflect = state["reflect"]

    try:
        exec(generation.imports)

    except Exception as e:
        error = "yes"
        messages += [("system", f"Encountered an error with import statement: {e}")]

        print(f"Error with import statement: {e}")
        return {"error": error, "messages": messages, "current_task": "An error has occured. Retrying Solution..."}

    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        exec(generation.code)

    except Exception as e:
        error = "yes"
        messages += [("system", f"Encountered an error with code block statement: {e}")]

        print(f"Error with code block: {e}")
        return {"error": error, "messages": messages, "current_task": "An error has occured. Retrying Solution..."}

    captured_output = captured_output.getvalue()
    sys.stdout = sys.__stdout__

    response = captured_output
    messages += [("system", f"Observation: {response}")]

    error = "no"

    if iterations > 2:
        reflect = "yes"

    print("-----NO CODE TEST FAILURES-----")
    return {"messages": messages, "error": error, "reflect": reflect, "current_task": "Typing Answer..."}

def reflect_code(state: GraphState):
    messages = state["messages"]

    messages += [
        (
            'system',
            """
            I tried to solve the problem and failed a unit test. I need to reflect on this failure based on the generated error.\n
            Write a few key suggestions to avoid making this mistake again.
            """,
        )
    ]

    reflections = code_chain.invoke({"messages": messages})
    messages += [("assistant", f"Here are reflections on the error: {reflections}")]

    return {"messages": messages}

def write_answer(state: GraphState):
    messages = state["messages"]
    response = state["response"]
    generation = state["generation"]

    result = analyst_chain.invoke({"messages": messages})

    response = result.ans
    messages += [("system", f"Here is the progress on the user's request: \n{response}")]

    generation_string = f"{generation.imports}\n{generation.code}"

    return {"response": response, "messages": messages, "current_task": "Closing...", "generation": f"{generation_string}"}

def should_end(state: GraphState):
    error = state["error"]
    iterations = state["iterations"]
    max_iters = state["max_iterations"]
    reflect = state["reflect"]
    messages = state["messages"]

    if error == "no" or iterations == max_iters:
        print("----DECISION: FINISH----")
        #print("Messages: \n", messages)
        return "end"
        

    else:
        print("----DECISION: RE-TRY SOLUTION----")
        if reflect == "yes":
            print("Reflecting on error...")
            return "reflect_code"

        else:
            return "planner"


print("\n Code successfully executed.\n")

wf = StateGraph(GraphState)

wf.add_node("planner", plan_steps)
wf.add_node("generate", generate_code)
wf.add_node("check_code", check_code)
wf.add_node("reflect_code", reflect_code)
wf.add_node("write_answer", write_answer)

wf.set_entry_point("planner")
wf.add_edge("planner", "generate")
wf.add_edge("generate", "check_code")
wf.add_conditional_edges(
    "check_code",
    should_end,
    {
        "end": "write_answer",
        "reflect_code": "reflect_code",
        "planner": "planner",
    }
)
wf.add_edge("reflect_code", "planner")
wf.add_edge("write_answer", END)

manipulate = wf.compile()

print("\nApp starts work here....\n")

#req = "reate a graph in the newsheet added based on the data in the first sheet. If you can't make the graph, print not possible."
source = '/Users/suryaganesan/Documents/GitHub/reporter/sales_data_copy.xlsx'


 
#response = app.invoke({"messages": [('user', formatted_req)], "request": req, "source_path": source, "max_iterations": 30, "iterations": 0})


def main():
    df = pd.read_excel(source)
    print(df.head())
    executions = []
    while True:
        req = input(">> ")
        formatted_req = format_request(req, source)
        temp = []

        inputs = {"messages": [('user', formatted_req)], "request": req, "source_path": source, "max_iterations": 3, "iterations": 0, "past_execs": executions}
        for event in manipulate.stream(inputs):
            for key, value in event.items():
                if key != "__END__":
                    print()

        #executions.append(temp[-1])
        df = pd.read_excel(source)
        executions.append({"request": req, "table": f"\n{df.head(5).to_string()}\n"})
        #print("Executions: \n", executions)
        #print("Length of temp: ", len(temp))
        #print("Temp: ", temp)
        df = pd.read_excel(source)
        print(df.head())


