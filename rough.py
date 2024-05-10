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

from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

# Setup

source = "sales_data_sample.xlsx"
secrets = "/Users/suryaganesan/Documents/GitHub/Replicate/secrets.toml"

os.environ["OPENAI_API_KEY"] = toml.load(secrets)["OPENAI_API_KEY"]

client = OpenAI()


# Code docs RAG

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/faiss_index"
db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 1})

response = retriever.invoke("Pivot tables")[0]
print(response.page_content)
print(len(response.page_content))