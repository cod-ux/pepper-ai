import os
import time

import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
from openpyxl import load_workbook

import xlwings as xl

from code_agents import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)


if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "ai", 
        "content": ""
        }]

def copy_excel_locally(file):
    fname, ext = os.path.splitext(file.name)
    new_fname = f"{fname}_copy{ext}"
    old_fname = f"{fname}{ext}"
    file_root = os.path.join("C:/Users/Administrator/Documents/github/reporter/uploads", new_fname)
    original_path = os.path.join("C:/Users/Administrator/Documents/github/reporter/", old_fname)
    with open(file_root, "wb") as local_file:
        local_file.write(file.read())
    st.success(f"File saved as {new_fname}")

    file_path = f"C:/Users/Administrator/Documents/github/reporter/uploads/{new_fname}"

    return file_path

def copy_excel_locally_from_path(file):
    fname, ext = os.path.splitext(file)
    new_fname = f"{fname}_copy{ext}"
    file_root = os.path.join("C:/Users/Administrator/Documents/github/reporter/uploads", new_fname)
    with open(file_root, "wb") as local_file:
        local_file.write(file.read())
    st.success(f"File saved as {new_fname}")

    file_path = f"C:/Users/Administrator/Documents/github/reporter/uploads/{new_fname}"

    return file_path


def handle_duplicate_columns(columns):
    counts = {}
    new_columns = []

    for col_name in columns:
        if col_name in counts:
            counts[col_name] += 1
            new_columns.append(f"{col_name}_{counts[col_name]}")
        else:
            counts[col_name] = 0
            new_columns.append(col_name)
    
    return new_columns


@st.cache_data()
def load_sheets_to_dfs(file_path):
    app = xl.App(visible=False)
    wb = app.books.open(file_path)
    dfs = []
    for sheet in wb.sheets:
        df = sheet.used_range.options(pd.DataFrame, header=True, index=True).value
        df.columns = handle_duplicate_columns(df.columns)
        dfs.append(df)

    sheet_names = [sheet.name for sheet in wb.sheets]
    wb.close()
    app.quit()
    return dfs, sheet_names


def save_sheets(path):
    app = xl.App(visible=False)
    book = app.books.open(path)
    book.save()
    book.close()
    app.kill()
    return True

# Main function
    # Upload Excel file
header_ph = st.empty()
header_ph.markdown( "<h3 style='text-align: center;'>Command AI: Spend less time preparing your data for analysis</h3>", unsafe_allow_html=True)
uploader_ph = st.empty()

with uploader_ph.container():
       uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

while uploaded_file is None:
    continue

def main():
    if "file_path" not in st.session_state:
        file_path = copy_excel_locally(uploaded_file)
        st.session_state.file_path = file_path
    else:
        file_path = st.session_state.file_path

    if file_path is not None:
        # Save excel file
        st.markdown("<h4>Current State: </h4>", unsafe_allow_html=True)
        st.sidebar.title("Excel sheets")
        
        dfs, sheets = load_sheets_to_dfs(file_path)

        select_sheet_ph = st.empty()

        with select_sheet_ph.container():
            current_sheet = st.sidebar.selectbox(
                "Select sheet",
                (sheets),
            )

        # Display current state
        current_table_placeholder = st.empty()

        with current_table_placeholder.container():
            st.dataframe(dfs[sheets.index(current_sheet)])

        request = st.chat_input("Enter your command...")
        
        if request:
            st.session_state.messages.append({"role": "human", "content": request})
            with st.chat_message("human"):
                st.write(request)

        if st.session_state.messages[-1]["role"] != "ai":
            if request:
               with st.chat_message("ai"):
                 if request != "quit":
                    test = save_sheets(file_path)
                    st.write(f"Saving and closing sheets: {test}")
                    st.write("Creating a plan...")
                    plan = create_plan(request, file_path)

                    st.write(f"The plan: \n{plan}")

                    st.write("Generating script")
                    script_generated = generate_code(request, file_path, plan)

                    st.code(f"Code generated: \n {script_generated}")
                    print("\n\nReviewing code...")

                    reviewed_script = review_code(request, script_generated, file_path, plan)

                    final_script = reviewed_script

                    st.code(f"#Script reviewed: \n{final_script}")

                    try:
                        st.write("\n\nInitiating code execution...")
                        exec(final_script)
                        status = save_sheets(st.session_state.file_path)
                        st.write(f"Saving changes: {status}")

                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.write("Analysing the error....")
                        new_code = refresh_code(request, e, file_path, plan, final_script)
                        st.code(f"New code: \n {new_code}")

                        try:
                            st.write("Initializing new refreshed code....")
                            exec(new_code)
                            status = save_sheets(st.session_state.file_path)
                            st.write(f"Saving changes: {status}")

                        except Exception as e2:
                            st.write(f"New Error: {e2}")

#        refresh = st.button("Refresh")
#        if refresh:
                        st.cache_data.clear()  

                        dfs, sheets = load_sheets_to_dfs(file_path)

                        print(dfs[0])
                        print(file_path)

                        current_table_placeholder.empty()
                        select_sheet_ph.empty()

                        with select_sheet_ph.container():
                            current_sheet = st.sidebar.selectbox(
                                "Select sheets",
                                (sheets),
                            )

                        with current_table_placeholder.container():
                            st.dataframe(dfs[sheets.index(current_sheet)])

if __name__ == "__main__":
    main()


        # Display current state
        

        

        





    # Create buttons for each sheet
    # if st.button show df for each sheet
