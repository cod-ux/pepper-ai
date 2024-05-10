import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from st_aggrid import AgGrid, GridOptionsBuilder
import json
import xlwings as xl
import xlrd

source = "/Users/suryaganesan/library/containers/com.microsoft.excel/data/test_book.xlsx"

@st.cache_data
# Function to edit and save Excel file
def edit_save_xl(file, cell_location, cell_value):
    # Change cell's value
    wb = load_workbook(file)
    ws = wb.active
    ws[cell_location] = cell_value
    wb.save(file)

@st.cache_data
def excel_to_df(file_path, sheet_name):
    # Load Excel file
    workbook = load_workbook(filename=file_path, data_only=True)
    sheet = workbook[sheet_name]

    # Convert Excel data to a list of dictionaries
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    # Convert list of dictionaries to JSON
    json_data = json.dumps(data[1:], indent=4)
    print(json_data[1])

    # Convert JSON to DataFrame
    df = pd.read_json(json_data)
    df.columns = data[0]

    return df

@st.cache_data
def df_from_excel(path):
    app = xl.App(visible=False)
    book = app.books.open(path)
    book.save()
    app.kill()
    return pd.read_excel(path)

def reload_excel():
    pass

# Main function
def main():
    # Upload Excel file
    uploader_ph = st.empty()
    uploaded_file = uploader_ph.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:

        # Read Excel file
        header_ph = st.empty()
        header_ph.header("Current State: ")
        df = df_from_excel(source)
        print("Before edit: ", df)

        sheets = st.selectbox(
            "Select sheet",
            ("Shee1", "Sheet2", "Sheet3")
        )

        # Display current state
        current_table_placeholder = st.empty()
        current_table_placeholder.dataframe(df)


    # Create buttons for each sheet
    # if st.button show df for each sheet



if __name__ == "__main__":
    main()
