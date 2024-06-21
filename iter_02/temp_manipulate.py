import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI
from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from utils import (
    query_llm_gpt4,
    extract_code_from_llm,
    load_excel_to_df,
    load_sheets_to_dfs
)



secrets = "/Users/suryaganesan/Documents/GitHub/reporter/secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

"""
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/Documents/GitHub/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 2}, )"""


def planner_template():

    system_msg = f"""
You are an intelligent assistant specializing in breaking down Excel file manipulation requests into clear, actionable tasks that can be executed by coding in python's openpyxl module. Analyze the user's request and create a concise list of steps to fulfill it:

Simple Requests: If it can be done in one step, condense it into one task.
Complex Requests: Break down into clear, specific, and actionable tasks. Detail what to do and how to do it.

Focus on essential tasks that a programmer should follow that  will directly achieve the user's goal. Avoid trivial steps like "Open the Excel file." Ensure tasks are descriptive enough to be executed without further clarification and keep the list brief.
Create a MAXIMUM of three tasks, NO MORE than that.
"""

    template = [
        (
            'system',
            system_msg
        ),
        (
            "placeholder",
            "{messages}"
        )
    ]

    prompt = ChatPromptTemplate.from_messages(template)

    return prompt


def format_request(request, source):
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\n\n"

    formatted = f"""
The user wants to execute their request on this excel file called: {source}.\n

------------
There are {len(dfs)} sheets in the excel file. Here is how the first few rows of those sheets look like:
{head_view}
------------

User request: {request}"""

    return formatted


def retrieve_context(request, retriever):
    code_examples = retriever.invoke(f"Documentation related to : {request}")
    content = [doc.page_content for doc in code_examples]
    seperator = "\n\n\n-----\n\n\n"
    conc_content = seperator.join(content)

    return conc_content

def code_chain_template():

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                """You are a coding assistant with expertise in Python's openpyxl module.\n
Fulfill the user request \n
by writing code for executing tasks that needs to be completed to achieve the end user request . Ensure that any code you provie can be executed \n
with all required imports and variables defined. Structure your response with a description of the code solution. \n
Then list the imports. And finally list the functioning code block. Always save the final output with the full source path name under the same name given in the plan when you make changes. \n
Here is the user's original request, progress on executing previous tasks, and the current task you need to write code to execute. Write code to execute the last retrieved task from the plan: """
            ),
            (
                'placeholder',
                '{messages}'
            )
        ]
    )

    return prompt


def format_code_request(task_to_be_executed):

    formatted = f"""
This is the current task I need to write code for executing the user request: {task_to_be_executed}\n

If there is any previous code then I need to rewrite it for it to execute the new additional task given to me. I need to make sure to use the entire source file path name as provided in previous messages to save the file.\n
And I should not use any dummy variables in the code. The code should be readily executable.
"""

    return formatted




def generate_code(request, source, plan):
    #code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    df = load_excel_to_df(source)
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\n\n"

    user_prompt = f"""
Write code to Import the file {source} with openpyxl and execute this user request: {request}

Use this step-by-step plan an excel user would use to achieve the final outcome:
{plan}

Do not use pandas. Save the final output again as {source}

There are {len(dfs)} sheets in the excel file. Here is how the first few rows of those sheets look like:
{head_view}

    """
    python_respone = extract_code_from_llm(query_llm_gpt4(user_prompt).content)

    return python_respone


def data_analyst_template():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                """You are a data analyst who understands data analytics and programming, who explains to the user the results of the program being executed to fulfill the user's request based on the history of messages given to you.\n
Provide a brief response to the user explaining how the system has executed the request and what the result was, \n
providing a logical and concise answer. Use the file name to indicate the modified file if necessary, but never use the full path of the file.\n
You don't have inform explicitly that the request has been executed by the system. If there was an error, then you can inform that there was an error, why there was an error and the final status of the execution.
"""
            ),
            (
                'placeholder',
                '{messages}'
            )
        ]
    )

    return prompt


