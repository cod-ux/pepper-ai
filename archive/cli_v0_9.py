import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import load_sheets_to_dfs
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from phoenix.trace.openai import OpenAIInstrumentor
import phoenix as px

from code_agents import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

# Setup

#session = px.launch_app()
source = "sales_data_sample.xlsx"
source_path = "sales_data_sample.xlsx"
secrets = "C:/Users/Administrator/Documents/reporter/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()

#OpenAIInstrumentor().instrument()

# Confirming source file

while True:
    try:
        wait = input(f"Excel source: {source}\nProceeding on confirmation...")
        dfs, sheet_names = load_sheets_to_dfs(source_path)
        for df in dfs:
            print("Df:")
            print(df.head(3))
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
            print("Creating a plan...")
            plan = create_plan(request, source_path)

            print(f"The plan: \n{plan}")

            print("Generating script")
            script_generated = generate_code(request, source_path, plan)

            print("Code generated: \n", script_generated)
            print("\n\nReviewing code...")

            reviewed_script = review_code(request, script_generated, source, plan)

            final_script = reviewed_script

            print(f"Script reviewed: \n{final_script}")

            try:
                print("\n\nInitiating code execution...")
                exec(final_script)

            except Exception as e:
                print(f"Error: {e}")
                print("Analysing the error....")
                new_code = refresh_code(request, e, source_path, plan, final_script)

                try:
                    print("Initializing new refreshed code....")
                    exec(new_code)

                except Exception as e2:
                    print(f"New Error: {e2}")


            dfs, sheet_names = load_sheets_to_dfs(source_path)
            for df in dfs:
                print("Df:")
                print(df.head(3))

        else:
            break


print("---------------EOP---------------")

# End of Program
