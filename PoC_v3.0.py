import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import (
    load_excel_to_json, 
    save_last_as_json, 
    query_llm, 
    extract_code_from_llm,
    load_excel_to_df
)

from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from phoenix.trace.openai import OpenAIInstrumentor
import phoenix as px

# Setup

session = px.launch_app()
source = "sales_data_sample.xlsx"
secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()

OpenAIInstrumentor().instrument()

# Code docs RAG

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 1})


def generate_code(request, source):
    #code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    df = load_excel_to_df(source)
    head_view = df.head().to_string(index=True)

    user_prompt = f"""
Write code to Import the file {source} with openpyxl and execute this user request: {request}

Do not use pandas. Save the final output again as {source}

Here is how the first few rows of the excel file looks like:
{head_view}

    """
    python_respone = extract_code_from_llm(query_llm(user_prompt).content)

    return python_respone

def review_code(request, code_response, source):
    code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    
    user_prompt = f"""
This was the user request: {request}

This is the code I am going to execute for the excel file called {source}:
{code_response}

Review and rewrite the code if there are any errors based on the openpyxl documentation given below:
{code_example}

Prefer to write excel formulas instead of doing manual data entry. If there is no error return the original code and save the file as {source}.
    """

    reviewed_code_response = extract_code_from_llm(query_llm(user_prompt).content)

    return reviewed_code_response

# Confirming source file

while True:
    try:
        wait = input(f"Excel source: {source}\nProceeding on confirmation...")
        df = load_excel_to_df(source)
        df_head = df.head().to_string()
        print("\nLength of Dataframe: ", len(df))
        break

    except Exception as e:
        print("Error: ", e)


# Application begins

print("--------------- COMMAND LINE -----------------")

while True:

    request = input(">> ")

    if request:
        if request != "quit":
            print("Generating script")
            script_generated = generate_code(request, source)

            #print("Code generated: \n", script_generated)
            #print("\n\nReviewing code...")

            final_script = script_generated

            print(f"Script reviewed: \n{final_script}")

            try:
                print("\n\nInitiating code execution...")
                exec(final_script)

            except Exception as e:
                print(f"Error: {e}")

        else:
            break



print("---------------EOP---------------")

# End of Program



