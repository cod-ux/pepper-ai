import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import (
    load_excel_to_json, 
    save_last_as_json, 
    query_llm, 
    extract_code
)


# Setup

source = "sales_data_sample.xlsx"
secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()

# Confirming source file

while True:
    try:
        wait = input(f"Excel source: {source}\nProceeding on confirmation...")
        json_text = load_excel_to_json(source)
        json_obj = json.loads(json_text)[:5]
        json_text = json.dumps(json_obj, indent=4)
        save_last_as_json(json_text)
        print("\nLength of JSON text: ", len(json_text))
        print("Print JSON object: \n", json_text)
        break

    except Exception as e:
        print("Error: ", e)


# Application begins

print("--------------- COMMAND LINE -----------------")

while True:

    request = input(">> ")
    with open("last_save.json", "r") as last_save:
        json_text = json.load(last_save)

    if request:
        if request != "quit" and request != "save":
            prompt = f"""Here are the first few rows of an excel file called {source} in its json format: \n{json_text}\n\n Provide ONLY the python code to execute the user's instructions. \nUser Instruction: {request}"""
            python_respone = query_llm(prompt)

            print("Code to be executed: \n", extract_code(python_respone.content))

            try:
                print("Initiating code execution...")
                exec(extract_code(python_respone.content))
                #print("Code: \n", extract_code(python_respone.content))

            except Exception as e:
                print(f"Error: {e}")

        else:
            break



print("---------------EOP---------------")

# End of Program



