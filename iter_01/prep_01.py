import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import openpyxl
import os

import xlwings as xl
#import phoenix as px
#from phoenix.trace.openai import OpenAIInstrumentor

from code_agents_01 import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

from streamlit_utils import copy_excel_locally, save_sheets, handle_duplicate_columns, unmerge_sheets, get_binary, undo, re_upload

st.set_page_config(layout="wide")

print("\nApp has reached here...")

#session = px.launch_app()
#OpenAIInstrumentor().instrument()

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


header_ph = st.empty()
header_ph.markdown( "<h3 style='text-align: center;'>Pepper, The Data Co-pilot</h3>", unsafe_allow_html=True)
st.markdown( "<h6 style='text-align: center;'>Automate repeatitive data tasks by coding in natural language</h6>", unsafe_allow_html=True)
st.markdown("<h3> </h3>", unsafe_allow_html=True)
uploader_ph = st.empty()
cache_clear = False


if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "ai", 
        "content": "Hello, operator. What can I do for you today?",
    }]

if "file_path" not in st.session_state:
   st.session_state.file_path = None

if "uploaded_file" not in st.session_state.keys():
    st.session_state.uploaded_file = None

if "cache_clear" not in st.session_state:
    st.session_state.cache_clear = False

if "state_stack" not in st.session_state:
    st.session_state.state_stack = [] # binaries of excels



uploaded_file = st.file_uploader("Upload or Select Excel file", ["xlsx", "xls"])
    
if uploaded_file is not None:    
    if st.session_state.file_path is None:
        print("\n------ B1 ------\n")
        print(f"Uploaded file says: {st.session_state.uploaded_file}")
        st.session_state.uploaded_file = uploaded_file
        print("\n------ B2 ------\n")
        print(f"Uploaded file says: {st.session_state.uploaded_file}")
        print(f"File path says: {st.session_state.file_path}")
        file_path = copy_excel_locally(st.session_state.uploaded_file)
        unmerge_sheets(file_path)
        st.session_state.file_path = file_path
        st.session_state.state_stack.append(get_binary(st.session_state.file_path))
        uploaded_file = None

#     Table view
    if st.session_state.file_path is not None:
            st.markdown("<h3 style='text-align: center;'></h3>", unsafe_allow_html=True)
            st.markdown( "<h6 style='text-align: center;'>Automate repeatitive data tasks by coding in natural language</h6>", unsafe_allow_html=True)
            print("\n------ B4 ------\n")
            print(f"Uploaded file says: {st.session_state.uploaded_file}")
            print(f"File path says: {st.session_state.file_path}")

            st.sidebar.title("Side Panel")

            
            
            st.markdown(f"<h5>{st.session_state.uploaded_file.name}: </h5>", unsafe_allow_html=True)
                
            
            dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

            select_sheet_ph = st.sidebar.empty()

            current_sheet = select_sheet_ph.radio("Select sheets", sheets)

            current_table_placeholder = st.empty()

            with current_table_placeholder.container(height=500):
                st.dataframe(dfs[sheets.index(current_sheet)], height=600)

    #     Chat box
            request = st.chat_input("Enter your code in natural language...")


            if request:
                    print("\n------ B5 ------\n")
                    st.session_state.messages.append({"role": "human", "content": request})
                    with st.chat_message("human"):
                            st.write(request)

#     Command execution

            if st.session_state.messages[-1]["role"] != "ai":
                    print("\n------ B6 ------\n")
                    if request:
                        with st.chat_message("ai"):
                            if request != "quit":
                                print("\n------ B7 ------\n")
                                st.session_state.state_stack.append(get_binary(st.session_state.file_path))
                                test = save_sheets(st.session_state.file_path)
                                st.caption("Creating a plan...")
                                print("Creating a plan...\n")
                                additional = create_plan(request, st.session_state.file_path)

                                #st.write(f"The plan: \n{plan}")
                                #print("The plan: \n", plan)

                                st.caption("Generating script...")
                                final_script = generate_code(request, st.session_state.file_path, additional)

                                #st.code(f"Code generated: \n {script_generated}")
                                print("The code: \n", final_script)
                                #print("\n\nReviewing code...")

                                #reviewed_script = review_code(request, script_generated, st.session_state.file_path, plan)

                                #final_script = reviewed_script

                                #st.code(f"#Script reviewed: \n{final_script}")
                                #print("Script reviewed: \n", final_script)

                                try:
                                    st.caption("\n\nInitiating code execution...")
                                    exec(final_script)
                                    status = save_sheets(st.session_state.file_path)
                                    st.write("...Request executed")
                                    message = {"role": "ai", "content": f"Successfully executed with: \n{final_script}"}
                                    print("\n------ B8 ------\n")
                                    #st.session_state.messages.append(message)
                                    cache_clear = True

                                except Exception as e:
                                    st.caption(f"Error: {e}")
                                    st.caption("Analysing the error....")
                                    print("Got error: ", e)

                                    new_code = refresh_code(request, e, st.session_state.file_path, final_script, additional)
                                    #st.code(f"New code: \n {new_code}")
                                    print("New code: ", new_code)

                                    try:
                                        st.caption("Initializing new refreshed code....")
                                        exec(new_code)
                                        status = save_sheets(st.session_state.file_path)
                                        st.write("Request Executed")
                                        message = {"role": "ai", "content": f"Successfully executed with: \n{str(final_script)}"}
                                        print("\n------ B8 ------\n")
                                        #st.session_state.messages.append(message)
                                        cache_clear = True

                                    except Exception as e2:
                                        st.caption(f"New Error: {e2}")
                                        message = {"role": "ai", "content": f"Execution unsuccessful due to error: \n{e2}"}
                                        #st.session_state.messages.append(message)
                                        print("Got a new error: ", e2)
                                        print("\n------ B9 ------\n")
                                
                                cache_clear = True

else:
    st.session_state.file_path = None
    st.session_state.uploaded_file = None
# Post execution

if cache_clear:
        print("\n------ B10 ------\n")
        
        st.sidebar.empty()
        st.cache_data.clear()
        current_sheet = None

        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

        print(dfs[0])
        print(st.session_state.file_path)

        current_table_placeholder.empty()
        select_sheet_ph.empty()


        current_sheet = st.empty()
                
        current_sheet = select_sheet_ph.radio("Select sheet",sheets)

        with current_table_placeholder.container(height=500):
            st.dataframe(dfs[sheets.index(current_sheet)], height=600)

        cache_clear = False

# side bar    
if st.session_state.file_path:
        print("\n------ B11 ------\n")
        if os.path.exists(st.session_state.file_path):
            print("\n------ B12 ------\n")
            st.sidebar.button("Undo", on_click=lambda: undo(st.session_state.file_path))
            st.sidebar.download_button(
                label = "Export",
                data = get_binary(st.session_state.file_path),
                file_name = os.path.basename(st.session_state.file_path),
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
                  

