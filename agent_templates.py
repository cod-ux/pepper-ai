import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import (
    query_llm_gpt4,
    extract_code_from_llm,
    load_excel_to_df,
    load_sheets_to_dfs
)

from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate


secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]


# Code docs RAG

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 2}, )

def plan_agent_template(request, source):
    #code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\n\n"

    user_prompt = f"""
For the given objective, come up with a simple step by step plan. \
This plan should involve individual takss, that if executed should yeild to the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Objective:
------------
The user wants to do the following to their excel file called {source}: {request}. \n
Finally save the file under the same name: {source}

There are {len(dfs)} sheets in the excel file. Here is how the first few rows of those sheets look like:
{head_view}
------------
"""

    return user_prompt



def retrieve_context(request, retriever=retriever):
    code_examples = retriever.invoke(f"Documentation related to : {request}")
    content = [doc.page_content for doc in code_examples]
    seperator = "\n\n\n-----\n\n\n"
    conc_content = seperator.join(content)

    return conc_content

def code_gen_template(request):

    context = retrieve_context(request=request)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                f"""You are a coding assistant with expertise in Python's openpyxl module.\n
                Here is a set of openpyxl documentation: \n --------- \n {context} \n --------- \n Answer the user question
                based on the above provided documentation. Ensure that any code you provie can be executed \n
                with all required imports and variables defined. Structure your answer with a description of the conde solution. \n
                Then list the imports. And finally list the functioning code block. Always save the final output with the full source path name under the same name given in the plan. \n
                Here is the user's request and a plan to follow to fulfill the user request: """
            ),
            (
                'placeholder',
                '{messages}'
            )
        ]
    )

    return prompt


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




