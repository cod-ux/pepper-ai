import os
import click
import xlwings as xw
import openpyxl
from openpyxl import load_workbook

from utils import load_sheets_to_dfs

from PoC_v3 import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

import streamlit as st
import pandas as pd

from phoenix.trace.openai import OpenAIInstrumentor
import phoenix as px

# Function to read Excel file
@st.cache_data
def read_excel_file(file):
    df = pd.read_excel(file, engine='openpyxl')
    return df

def main():
    st.title("Command AI: A simple way to clean & Manipulate your excel")
    
    # Input fields
    api_key_placeholder = st.empty()
    api_key = api_key_placeholder.text_input("Enter your OpenAI API key:")
    
    uploaded_file_placeholder = st.empty()
    uploaded_file = uploaded_file_placeholder.file_uploader("Upload Excel file", type=['xlsx', 'xls'])

    
    
    # Continue button
    if st.button("Continue"):
        df_window = st.empty()
        if not api_key:
            st.warning("Please enter your OpenAI API key.")
        elif not uploaded_file:
            st.warning("Please upload an Excel file.")
        else:
            # Hide input fields
            api_key_placeholder.empty()
            uploaded_file_placeholder.empty()
            
            # Read and display Excel file
            df = read_excel_file(uploaded_file)
            
            # Dropdown to navigate between different sheets
            sheet_names = pd.ExcelFile(uploaded_file).sheet_names
            sheet_name = st.selectbox("Select a sheet", sheet_names)
            df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine='openpyxl')
            df_window.dataframe(df_sheet)

if __name__ == "__main__":
    main()
