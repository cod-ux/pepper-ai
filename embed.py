from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_openai.embeddings import OpenAIEmbeddings

import pandas as pd
import os
import toml
import os

secrets_path = "/Users/suryaganesan/Documents/GitHub/im_rag/im_rag/secrets.toml"

model_name = "text-embedding-ada-002"
model_name_2 = "text-embedding-3-large"

os.environ["OPENAI_API_KEY"] = toml.load(secrets_path)["OPENAI_API_KEY"]

source_path = "/Users/suryaganesan/vscode/ml/projects/reporter/RAG_docs/"

def list_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_list.append(os.path.join(root, file_name))
    return file_list

directory = "/Users/suryaganesan/vscode/ml/projects/reporter/RAG_docs/"
files = list_files(directory)


page_list = []
for file_path in files:
    load = PyPDFLoader(file_path)
    pages = load.load()
    content_holder = ''
    for page in pages:
        content_holder += page.page_content
        content_holder += "\n\n\n --- \n\n\n"
    print(content_holder)
    page_list.append(content_holder)


#print(len(page_list[0].page_content))
print(type(page_list[0]))


print("No. of docs: ", len(page_list))
print("Length of doc: ", len(page_list[0]))

## Embed and export text_chunks to faiss_index - For im_rag retrieval

print("Embedding chunks and exporting to faiss...")

#embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/"

#db = FAISS.from_documents(page_list, embeddings)
db = FAISS.from_texts(page_list, embeddings)
db.save_local(path+'faiss_index')

print("...Program terminated")