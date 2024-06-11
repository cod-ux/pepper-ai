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



secrets = "/home/ubuntu/Github/reporter/secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]


def planner_template():

    system_msg = f"""
You are an intelligent data analyst specializing in answering Excel file exploration related questions by making a plan with clear, actionable tasks that can be executed by coding in python's Pandas and seaborn modules (if graph's are involved) to answer the user question about the excel file.
Analyze the user's request and create a concise list of steps a programmer should follow to fulfill the exploration question:

Follow these guidelines:
- Focus on essential tasks that directly achieve the user's goal. Avoid trivial steps like "Open the Excel file." Ensure tasks are descriptive enough to be executed without further clarification and keeps the list brief.
- The last step should ALWAYS be returning your findings by either printing them, if its text, or displaying chart if the output is a graph.
- If the user questions is instead a request to change any source data from the excel file, Abandon all operations and ONLY print that you can only answer questions in the "explore" mode and can't manipulate the data. \n
- The last section of the program should always be a print statement that provides a meaningful word response to the user question.
- Try not to print the dataframe or its head in the answers
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
The user wants to find an answer to their question regarding this excel file called: {source}.\n

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
                """You are a coding assistant with expertise in Python's pandas module and seaborn module.\n
Answer the user question about the excel file by writing code for executing each task from the generated plan. Ensure that any code you provie can be executed \n
with all required imports and variables defined. Structure your response with a description of the code solution. \n
Then list the imports. And finally list the functioning code block. NEVER make any changes to the source excel file. \n

If the user questions is instead a request to change any source data from the excel file, ONLY write the python code to print that you can only answer questions in "explore" mode and can't manipulate the data. \n


Remember that you are in a streamlit envirnonment, so follow the guidelines when returning the results:
- ALWAYS do return the python code to import pandas, even if code is not required. \n
- ALWAYS do print the answer that you find at the end of the program. This will provide the user with the answer to their question. \n
- ALWAYS do save any graphs you make with seaborn as images in the folder "/home/ubuntu/Github/reporter/ph_images" at the end of the program. This will provide the user with the answer to their question. \n
- ALWAYS do write code to create some sort of a graph whenever the user asks for wrtiting a graph. \n

Here is the user's original question, progress on executing previous tasks, and the current task you need to write code to execute. Write code to execute the last retrieved task from the plan: """
            ),
            (
                'placeholder',
                '{messages}'
            )
        ]
    )

    return prompt

def coding_temp_v2():
    prompt = """
### PREVIOUS CONVERSATIONS
{past_conversations}

{dfs_list}



Update this initial code:
```python
# TODO: Import required dependencies
from openpyxl import load_workbook
import openpyxl

# Load workbook


# Write code here


# Delcare result var: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }


# Save workbook with the same source_file name.

```

### QUERY
{query} 

At the end, declare "result" variable as a dictionary of type and value.

If you are asked to plot a chart, use "matplotlib" for charts, save as png at 'exports' folder as temp_chart.png.

Answer the user question about the excel file by writing python code. Ensure that any code you provie can be executed. \n

Generate python code and return full updated code:
"""

    return prompt

def data_analyst_template():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                """You are a data analyst who is an expert in understanding data and coding, and provides logical answers to user questions.\n
Answer the user question about the excel file by referring to the conversation between the user and the system, \n
providing a logical and concise answer to the user's question. \n
Do not explain the code or return any code in the final answer. \n
Do provide a status update on whether or not the system was able to execute the request and if any errors, explain why the system got into an error. \n

Never include any file path names or information about saving images in the final response: """
            ),
            (
                'placeholder',
                '{messages}'
            )
        ]
    )

    return prompt


