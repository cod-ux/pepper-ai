# Catch pandasai in phoenix
import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor
from pandasai import SmartDatalake
from langchain_openai import OpenAI
from explore.utils import load_sheets_to_dfs
import pandas as pd
import toml
import os

session = px.launch_app()
LangChainInstrumentor().instrument()

secrets = "C:/Users/Administrator/Documents/github/reporter/secrets.toml"
os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]
llm = OpenAI()

source = 'C:/Users/Administrator/Documents/github/reporter/excel_source/sales_data_copy.xlsx'
dfs, _ = load_sheets_to_dfs(source)
lake = SmartDatalake(dfs, config={"llm": llm})


while True:
    query = input(">>")
    response = lake.chat(query)
    print(response)
