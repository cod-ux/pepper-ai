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



secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

"""
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 2}, )"""


def planner_template():

    system_msg = f"""
You are an intelligent assistant that identifies individual tasks that needs to be fulfilled to execute the user request that involve manipulating Excel files. \n
Your task is to analyze the user's request and break it down into executable tasks. Follow these guidelines:

Simple Requests: If the user request is straightforward and can be achieved with a single task, provide only one task.

Example: For a request like "Create a new column at the end by copying the last column and pasting it again," you would return:
"Copy the last column and paste it at the end of the table."\n

Complex Requests: If the user request is more complex and requires multiple tasks to achieve the desired outcome, provide a detailed list of tasks.
Each task should be clear, actionable, and logically sequenced.

Example: For a request like "Create a new column by using VLOOKUP formula and look up the sale value information from Sheet2 based on opportunity ID column in both sheets," you might return:
"Identify the opportunity ID column in both Sheet1 and Sheet2."
"Insert a new column in Sheet1 where the VLOOKUP formula will be applied."
"Enter the VLOOKUP formula in the new column to fetch sales value information from Sheet2 based on the opportunity ID."
"Copy the VLOOKUP formula down the entire column to apply it to all rows."

Do not add superfluous steps like "Open the excel sheet" or "Save the excel sheet".
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

def review_code(request, code_response, source, plan):
    code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    
    user_prompt = f"""
This was the user request: {request}

This is the code I am going to execute for the excel file called {source}:
{code_response}

Here is the plan used to create this code. Review and if necessary rewrite the code to make sure the code follows the plan as much as possible:
{plan}

Here is some relevant openpyxl documntation texts. Review and rewrite the code to make sure there are NO errors:
{code_example}


Prefer to write excel formulas instead of doing manual data entry. If there is no error return the original code and save the file as {source}.
Prefer to use move_range() function if the user asks to move columns.
ONLY RETURN CODE AS OUTPUTS, NO NEED FOR EXPLANATIONS.
    """

    reviewed_code_response = extract_code_from_llm(query_llm_gpt4(user_prompt).content)

    return reviewed_code_response

def refresh_code(request, error, source, plan, old_code):
    code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    
    user_prompt = f"""
This was the user request: {request}

This is the code I tried to execute on the excel file called {source}:
{old_code}

Here is the plan I wanted to execute to through this code. Review and if necessary rewrite the code to make sure the code follows the plan as much as possible:
{plan}

Here is some relevant openpyxl documntation texts. Review and rewrite the code to make sure there are NO errors:
{code_example}


Prefer to write excel formulas instead of doing manual data entry. If there is no error return the original code and save the file as {source}.
Prefer to use move_range() function if the user asks to move columns.
ONLY RETURN CODE AS OUTPUTS, NO NEED FOR EXPLANATIONS.
    """

    refreshed_code_response = extract_code_from_llm(query_llm_gpt4(user_prompt).content)

    return refreshed_code_response




