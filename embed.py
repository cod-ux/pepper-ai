from langchain.document_loaders import DirectoryLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_openai.embeddings import OpenAIEmbeddings

import pandas as pd
import os
import toml

## Load documents

secrets_path = "/Users/suryaganesan/Documents/GitHub/im_rag/im_rag/secrets.toml"

model_name = "text-embedding-ada-002"
model_name_2 = "text-embedding-3-large"

os.environ["OPENAI_API_KEY"] = toml.load(secrets_path)["OPENAI_API_KEY"]

source_path = "/Users/suryaganesan/vscode/ml/projects/reporter/RAG_docs/"
md_loader = DirectoryLoader(source_path)

md_documents = md_loader.load()

print("No. of docs: ", len(md_documents))

####### Split documents

"""mark_down_splitter = MarkdownHeaderTextSplitter(headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
])"""

character_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1500,
    chunk_overlap = 225,
    length_function = len,
    is_separator_regex = False,
)

content = [doc.page_content for doc in md_documents]
seperator = "\n"
content = seperator.join(content)


#text_chunks = mark_down_splitter.split_text(content)
text_chunks = character_text_splitter.split_text(content)
text_chunks = character_text_splitter.create_documents(text_chunks)


print("No. of text chunks: ", len(text_chunks))

## Embed and export text_chunks to faiss_index - For im_rag retrieval

print("Embedding chunks and exporting to faiss...")

#embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
path = "/Users/suryaganesan/vscode/ml/projects/reporter/"

db = FAISS.from_documents(text_chunks, embeddings)
db.save_local(path+'faiss_index')

print("...Program terminated")