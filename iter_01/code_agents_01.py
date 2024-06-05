import os
import toml
import json

from openpyxl import load_workbook
from openai import OpenAI

from utils import (
    query_llm_gpt4,
    query_llm_gpt35,
    query_llm_gpt35_chat, 
    extract_code_from_llm,
    load_excel_to_df,
    load_sheets_to_dfs
)

from langchain.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings


# Setup

source = "sales_data_sample.xlsx"
source_path = "sales_data_sample.xlsx"
secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()


# Code docs RAG

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 1})

def create_plan(request, source):
    #code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\nTotal no. of columns in the sheet: {len(df.columns)}\n\n"

    user_prompt = f"""
### GOAL
Make a list of the variables required to write a program for executing the following user request. \n
ONLY provide the variables as copy pasteable TEXT, DO NOT provide any other explanations. \n
If the variable values are known, assign those values. If they are to be calculated during run time, assign '#To be calculated' for the variable values\n 

### USER REQUEST
{request}

### EXCEL DATA SAMPLE
Note: This is only a sample data, there are more rows in these sheets than being shown here.

There are {len(dfs)} sheets in the excel file saved at {source}. \n
Here is how the first few rows of those sheets look like: \n
{head_view}

### VARIABLES REQUIRED

"""
    response = query_llm_gpt4(user_prompt)
    print(f"Unaltered LLM response: \n{response}")
    plan = response.content

    return plan


def generate_code(request, source, additional):
    code_example = retriever.invoke(f"{request}")[0].page_content
    dfs, sheet_names = load_sheets_to_dfs(source)
    head_view = ''

    for i, df in enumerate(dfs):
        head_view += f"\nSheet {i}: {sheet_names[i]}\nSheet head:\n{df.head(3)}\n\n"

    user_prompt = f"""
### USER REQUEST
Write code to execute this user request: {request}

### INSTRUCTIONS
DONT USE PANDAS
ONLY use openpyxlmodule for loading excel data
Import this file in your code and save the final output again in the same name as this file: {source}. 
Provide ONLY the python source code as a response.
Import ALL Necessary libraries in the code.
Use the excel sheet information given below to identify sheet names and column names for variables in the code. 
Explicitly specify sheet names and column names instead of relying on sheet and column order based on given info on the excel sheets below.

### ADDITIONAL INFORMATION
{additional}

### EXCEL DATA SAMPLE
--- Excel Sheet head views ---

There are {len(dfs)} sheets in the excel file. Here is how the first few rows of those sheets look like:
{head_view}

### CODE SOLUTION
ONLY provide the executable code. You will be penalised if you provide anything other than the CODE to execute the request. \n

Code Solution:

"""
    response = query_llm_gpt4(user_prompt)
    code = extract_code_from_llm(response.content)


    return code

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

    python_respone = query_llm_gpt35(user_prompt)
    print(f"Unaltered LLM response: \n{python_respone}")
    python_respone = python_respone

    return python_respone

def refresh_code(request, error, source, old_code, additional):
    code_example = retriever.invoke(f"Find a python code example relating to: {request}")[0].page_content
    
    user_prompt = f"""
This was the user request: {request}

This is the code I tried to execute on the excel file called {source}:
{old_code}

This is the error that I ran into : {error}

Additional information about excel file:
{additional}

Instructions to follow:
DONT USE PANDAS
If there is no error return the original code and save the file as {source}.
Try to write python code, over relying on excel formulas.
Prefer to use move_range() function if the user asks to move columns.
Explicitly specify sheet names and column names instead of relying on sheet and column order based on given info on the excel sheets below.

ONLY RETURN CODE AS OUTPUTS, NO NEED FOR EXPLANATIONS.
    """

    response = query_llm_gpt4(user_prompt)
    code = extract_code_from_llm(response.content)

    return code





"""
Ideal prompt:

<dataframe>
dfs[0]:10406x22
ORDERNUMBER,QUANTITYORDERED,DEALSIZE,ORDERLINENUMBER,SALES,ORDERDATE,STATUS,QTR_ID,MONTH_ID,YEAR_ID,PRODUCTLINE,MSRP,PRODUCTCODE,CUSTOMERNAME,PHONE,ADDRESSLINE1,ADDRESSLINE2,CITY,STATE,POSTALCODE,COUNTRY,TERRITORY
10145.0,35.0,,,5756.52,,In Process,QTR_ID,,,Classic Cars,118,,"Dragon Souveniers, Ltd.",0033383230,11328 Douglas Av.,,Newark,,50553,Japan,
,20.0,Small,11.0,,4/8/2005 0:00,,,10.0,2003,,MSRP,PRODUCTCODE,Gift Depot Inc.,6698603660,,Level 15,Torino,Osaka,44000,UK,Japan
10126.0,,Large,12.0,4860.24,11/6/2003 0:00,Disputed,2,7.0,YEAR_ID,PRODUCTLINE,,S10_4698,,2089168840,9408 Furth Circle,ADDRESSLINE2,,Tokyo,,,TERRITORY
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }

```



### QUERY
 How many entries do we have?

Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.

Generate python code and return full updated code:

"""