import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from st_aggrid import AgGrid, GridOptionsBuilder
import json
import xlwings as xl
import xlrd

import streamlit as st
import pandas as pd
import pygsheets

source = "/Users/suryaganesan/downloads/test_book.xlsx"

# Function to upload Excel file to Google Sheets
def upload_to_google_sheets(uploaded_file):
    # Authorization
    gc = pygsheets.authorize(service_file='sheets_account.json')

    # Open the Google Spreadsheet
    sh = gc.create("uploaded_file.xlsx")
    wks = sh[0]
    # Upload Excel file to Google Sheets
    df = pd.read_excel(uploaded_file)
    wks.set_dataframe(df, (1,1))

    return sh

# Function to perform operations on the Google Sheet
def perform_operations(sh):
    # Access the first sheet
    wks = sh[0]

    # Read data from Google Sheet
    df = wks.get_as_df()

    # Perform operations
    st.write("Data from Google Sheet:")
    st.write(df)

# Main function
def main():
    st.title("Upload Excel File to Google Sheets")

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    # Check if file is uploaded
    if uploaded_file is not None:
        # Upload Excel file to Google Sheets
        sh = upload_to_google_sheets(uploaded_file)
        print(sh.url)
        print("Upload successful...")
        # Perform operations on Google Sheet
        perform_operations(sh)

if __name__ == "__main__":
    main()
