import os
import time

import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
from openpyxl import load_workbook

import xlwings as xl

from PoC_v3 import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)


def copy_excel_locally(file):
    fname, ext = os.path.splitext(file.name)
    new_fname = f"{fname}_copy{ext}"
    old_fname = f"{fname}{ext}"
    file_root = os.path.join("/Users/suryaganesan/vscode/ml/projects/reporter/uploads", new_fname)
    original_path = os.path.join("/Users/suryaganesan/vscode/ml/projects/reporter/", old_fname)
    with open(file_root, "wb") as local_file:
        local_file.write(file.read())
    st.success(f"File saved as {new_fname}")

    file_path = f"/Users/suryaganesan/vscode/ml/projects/reporter/uploads/{new_fname}"

    return file_path

def copy_excel_locally_from_path(file):
    fname, ext = os.path.splitext(file)
    new_fname = f"{fname}_copy{ext}"
    file_root = os.path.join("/Users/suryaganesan/vscode/ml/projects/reporter/uploads", new_fname)
    with open(file_root, "wb") as local_file:
        local_file.write(file.read())
    st.success(f"File saved as {new_fname}")

    file_path = f"/Users/suryaganesan/vscode/ml/projects/reporter/uploads/{new_fname}"

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
        df = sheet.used_range.options(pd.DataFrame, header=True, index=False).value
        df.columns = handle_duplicate_columns(df.columns)
        dfs.append(df)

    sheet_names = [sheet.name for sheet in wb.sheets]
    wb.save()
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

# Two errors to fix:
# 1. If I delete uploaded file, it still retains it to work on
# 2. Not saving after change

select_sheet_key = "select-sheet"

if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "ai", 
        "content": ""
    }]

if "file_path" not in st.session_state:
   st.session_state.file_path = None

if "cache_clear" not in st.session_state:
    st.session_state.cache_clear = False


def sheet_choice_01(sheets_list):
    return st.sidebar.selectbox(
        "Select sheet",
        sheets_list
    )


def main():
    global cache_clear

    with uploader_ph.container():
       uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is None:
        st.session_state.file_path = None

    if uploaded_file is not None:
        if st.session_state.file_path is None:
            file_path = copy_excel_locally(uploaded_file)
            st.session_state.file_path = file_path

#      if st.session_state.file_path is not None:
        # Save excel file
        st.markdown("<h4>Current State: </h4>", unsafe_allow_html=True)
        st.sidebar.title("Excel sheets")
        
        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

        select_sheet_ph = st.sidebar.empty()

        current_sheet = select_sheet_ph.radio("Select sheets", sheets)

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
                    test = save_sheets(st.session_state.file_path)
                    st.write(f"Saving and closing sheet: {test}")
                    st.write("Creating a plan...")
                    print("Creating a plan...\n")
                    plan = create_plan(request, st.session_state.file_path)

                    st.write(f"The plan: \n{plan}")
                    print("The plan: \n", plan)

                    st.write("Generating script")
                    script_generated = generate_code(request, st.session_state.file_path, plan)

                    st.code(f"Code generated: \n {script_generated}")
                    print("The code: \n", script_generated)
                    print("\n\nReviewing code...")

                    reviewed_script = review_code(request, script_generated, st.session_state.file_path, plan)

                    final_script = reviewed_script

                    st.code(f"#Script reviewed: \n{final_script}")
                    print("Script reviewed: \n", final_script)

                    try:
                        st.write("\n\nInitiating code execution...")
                        exec(final_script)
                        status = save_sheets(st.session_state.file_path)
                        st.write(f"Saving changes: {status}")
                        message = {"role": "ai", "content": f"{final_script}"}
                        st.session_state.messages.append(message)
                        cache_clear = True

                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.write("Analysing the error....")
                        print("Got error: ", e)

                        new_code = refresh_code(request, e, st.session_state.file_path, plan, final_script)
                        st.code(f"New code: \n {new_code}")
                        print("New code: ", new_code)

                        try:
                            st.write("Initializing new refreshed code....")
                            exec(new_code)
                            status = save_sheets(st.session_state.file_path)
                            st.write(f"Saving changes: {status}")
                            message = {"role": "ai", "content": f"{final_script}"}
                            st.session_state.messages.append(message)
                            cache_clear = True

                        except Exception as e2:
                            st.write(f"New Error: {e2}")
                            print("Got a new error: ", e2)
                    
                    cache_clear = True

    if cache_clear:
                  st.sidebar.empty()
                  st.cache_data.clear()
                  current_sheet = None

                  with st.chat_message("ai"):
                    st.write("Cache data should be cleared")

                  dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

                  print(dfs[0])
                  print(st.session_state.file_path)

                  current_table_placeholder.empty()
                  select_sheet_ph.empty()


                  current_sheet = st.empty()
                
                  current_sheet = select_sheet_ph.radio("Select sheet",sheets)

                  with current_table_placeholder.container():
                      st.dataframe(dfs[sheets.index(current_sheet)])

                  cache_clear = False

                  

if __name__ == "__main__":
    cache_clear = False
    main()

# If encountered error, use saved intermediate steps to continue