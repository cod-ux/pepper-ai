import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import os

import xlwings as xl

from code_agents import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

from streamlit_utils import copy_excel_locally, save_sheets, load_sheets_to_dfs, unmerge_sheets, get_binary, undo


header_ph = st.empty()
header_ph.markdown( "<h3 style='text-align: center;'>Command AI: Spend less time preparing your data for analysis</h3>", unsafe_allow_html=True)
uploader_ph = st.empty()

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

if "state_stack" not in st.session_state:
    st.session_state.state_stack = [] # binaries of excels


def main():
    global cache_clear

# Upload excel

    with uploader_ph.container():
       uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is None:
        st.session_state.file_path = None

    if uploaded_file is not None:
        if st.session_state.file_path is None:
            file_path = copy_excel_locally(uploaded_file)
            unmerge_sheets(file_path)
            st.session_state.file_path = file_path
            st.session_state.state_stack.append(get_binary(st.session_state.file_path))
            

# User Interface:
#     Table view

        st.markdown("<h4>Table view: </h4>", unsafe_allow_html=True)
        st.sidebar.title("Excel sheets")
        
        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

        select_sheet_ph = st.sidebar.empty()

        current_sheet = select_sheet_ph.radio("Select sheets", sheets)

        current_table_placeholder = st.empty()

        with current_table_placeholder.container():
            st.dataframe(dfs[sheets.index(current_sheet)])

#     Chat box

        request = st.chat_input("Enter your command...")
        
        if request:
            st.session_state.messages.append({"role": "human", "content": request})
            with st.chat_message("human"):
                st.write(request)

#     Command execution

        if st.session_state.messages[-1]["role"] != "ai":
            if request:
                with st.chat_message("ai"):
                  if request != "quit":
                    st.session_state.state_stack.append(get_binary(st.session_state.file_path))
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

# Post execution

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

# side bar    
    if st.session_state.file_path:
        if os.path.exists(st.session_state.file_path):
            st.sidebar.button("Undo", on_click=lambda: undo(st.session_state.file_path))
            st.sidebar.download_button(
                label = "Export",
                data = get_binary(st.session_state.file_path),
                file_name = os.path.basename(st.session_state.file_path),
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
                  

if __name__ == "__main__":
    cache_clear = False
    main()
