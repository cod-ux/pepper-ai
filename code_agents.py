import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import (
    query_llm_gpt4,
    query_llm_gpt35, 
    extract_code_from_llm,
    load_excel_to_df,
    load_sheets_to_dfs
)

from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings


# Setup

source = "sales_data_sample.xlsx"
source_path = "sales_data_sample.xlsx"
secrets = "/Github/reporter/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()


# Code docs RAG

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Github/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 1})

def create_plan(request, source):
    #code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    df = load_excel_to_df(source)
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\n\n"

    user_prompt = f"""
The user wants to do the following to their excel file called {source}: {request}.

Create a plan for how an excel user can achieve the end goal by breaking the goal down into a list of simple executable steps, which when executed should perfectly fullfill the user's request.

The output should be ONLY be a list of steps that needs to be taken. No explanantion is required.
ALWAYS save the file under the same name: {source}

There are {len(dfs)} sheets in the excel file. Here is how the first few rows of those sheets look like:
{head_view}
    """
    plan = extract_code_from_llm(query_llm_gpt4(user_prompt).content)

    return plan


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




