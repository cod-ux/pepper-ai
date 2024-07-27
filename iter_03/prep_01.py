import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import openpyxl
import os, time

import xlwings as xl
#import phoenix as px
#from phoenix.trace.openai import OpenAIInstrumentor

from code_agents_01 import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

from streamlit_utils import copy_excel_locally, save_sheets, split_numbered_list, unmerge_sheets, get_binary, undo, load_sheets_to_dfs

st.set_page_config(layout="wide")

print("\nApp has reached here...")

#session = px.launch_app()
#OpenAIInstrumentor().instrument()

header_ph = st.empty()
header_ph.markdown( "<h3 style='text-align: center;'>Pepper, Your Data Co-Pilot 🤖</h3>", unsafe_allow_html=True)
st.markdown( "<h6 style='text-align: center;'>Spend more time with <span style='text-decoration: line-through; text-decoration-color: orange;'>bad</span> clean data</h6>", unsafe_allow_html=True)
st.markdown("<h4> </h4>", unsafe_allow_html=True)
uploader_ph = st.empty()
cache_clear = False


if 'key' not in st.session_state:
    st.session_state.key = 'value'

if 'dev_mode' not in st.session_state:
    st.session_state.dev_mode = False

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "ai", "content": "..."}]

if "text_chain_3" not in st.session_state.keys():
    st.session_state.text_chain_3 = None

if "text_chain_2" not in st.session_state.keys():
    st.session_state.text_chain_2 = None

if "text_chain_1" not in st.session_state.keys():
    st.session_state.text_chain_1 = None

if 'continue_clicked' not in st.session_state:
    st.session_state.continue_clicked = False

if 'user_input' not in st.session_state:
    st.session_state.user_input = None

if 'request' not in st.session_state:
    st.session_state.request = None

if 'temp_input' not in st.session_state:
    st.session_state.temp_input = None

if "file_path" not in st.session_state:
   st.session_state.file_path = None

if "uploaded_file" not in st.session_state.keys():
    st.session_state.uploaded_file = None

if "cache_clear" not in st.session_state:
    st.session_state.cache_clear = False

if "state_stack" not in st.session_state:
    st.session_state.state_stack = [] # binaries of excels

if "past_execs" not in st.session_state:
    st.session_state.past_execs = ""

if "additional" not in st.session_state:
    st.session_state.additional = None


def display_code_editor():
    code_editor = st.empty()
    st.session_state.temp_input = code_editor.text_area("Code", final_script)
    st.button("Continue", on_click=handle_continue)

def handle_continue():
    #temp_input = st.session_state.temp_input
    st.session_state.user_input = st.session_state.temp_input
    print(f"continue clicked: {st.session_state.continue_clicked}")
    st.session_state.continue_clicked = True
    #st.rerun()

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
            st.markdown("<h4 style='text-align: center;'></h4>", unsafe_allow_html=True)
            #st.markdown( "<h6 style='text-align: center;'>Automate repeatitive data tasks by coding in natural language</h6>", unsafe_allow_html=True)
            print("\n------ B4 ------\n")
            print(f"Uploaded file says: {st.session_state.uploaded_file}")
            print(f"File path says: {st.session_state.file_path}")

            st.sidebar.title("Side Panel")
            
            st.markdown(f"<h5>{st.session_state.uploaded_file.name}: </h5>", unsafe_allow_html=True)
                
            
            dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

            select_sheet_ph = st.sidebar.empty()

            current_sheet = select_sheet_ph.radio("Select sheets", sheets)

            current_table_placeholder = st.empty()


            current_table_placeholder.dataframe(dfs[sheets.index(current_sheet)], height=500)

    #     Chat box
            st.session_state.request = st.chat_input("Enter your code in natural language...")

            

            msg_length_0 = len(st.session_state.messages)

            if st.session_state.request:
                    print("\n------ B5 ------\n")
                    st.session_state.messages.append({"role": "human", "content": st.session_state.request})

            

#     Command execution

            if st.session_state.messages[-1]["role"] != "ai":
                    print("\n------ B6 ------\n")
                    print(f"continue clicked: {st.session_state.continue_clicked}")

                    if st.session_state.dev_mode:
                        text_chain_1 = st.empty()
                        text_chain_2 = st.empty()
                        
                        with text_chain_1.chat_message("ai"):
                            if st.session_state.request:
                                if st.session_state.request != "quit":
                                    st.caption(f"Executing: {st.session_state.request}")
                                    print("\n------ B7 ------\n")
                                    st.session_state.state_stack.append(get_binary(st.session_state.file_path))
                                    test = save_sheets(st.session_state.file_path)
                                    #request_list = split_numbered_list(request)
                                    #print(f"Request list:\n {request_list}")
                                    #for req in request_list:
                                        #request = req
                                        #st.caption(f"Executing: {request}")
                                    
                                    st.caption("Creating a plan...")
                                    print("Creating a plan...\n")
                                    st.session_state.additional = create_plan(st.session_state.request, st.session_state.file_path)

                                    #st.write(f"The plan: \n{plan}")
                                    #print("The plan: \n", plan)

                                    st.caption("Generating script...")
                                    final_script = generate_code(st.session_state.request, st.session_state.file_path, st.session_state.additional)

                                    #st.code(f"Code generated: \n {script_generated}")
                                    print("The code: \n", final_script)

                                    if not st.session_state.continue_clicked:
                                        display_code_editor()

                    if not st.session_state.dev_mode:        
                        if st.session_state.request:
                            st.session_state.text_chain_3 = st.empty()
                            with st.session_state.text_chain_3.chat_message("ai"):
                                if st.session_state.request != "quit":
                                    print("\n------ B7 ------\n")
                                    st.session_state.state_stack.append(get_binary(st.session_state.file_path))
                                    test = save_sheets(st.session_state.file_path)
                                    request_list = split_numbered_list(st.session_state.request)
                                    print(f"Request list:\n {request_list}")
                                    for req in request_list:
                                        request = req
                                        st.caption(f"Executing: {request}")
                                        st.caption("Creating a plan...")
                                        print("Creating a plan...\n")
                                        st.session_state.additional = create_plan(request, st.session_state.file_path)

                                        #st.write(f"The plan: \n{plan}")
                                        #print("The plan: \n", plan)

                                        st.caption("Generating script...")
                                        final_script = generate_code(request, st.session_state.file_path, st.session_state.additional)

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
                                            

                                        except Exception as e:
                                            st.caption(f"Error: {e}")
                                            st.caption("Analysing the error....")
                                            print("Got error: ", e)

                                            new_code = refresh_code(request, e, st.session_state.file_path, final_script, st.session_state.additional)
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
                                                

                                            except Exception as e2:
                                                st.caption(f"New Error: {e2}")
                                                message = {"role": "ai", "content": f"Execution unsuccessful due to error: \n{e2}"}
                                                #st.session_state.messages.append(message)
                                                print("Got a new error: ", e2)
                                                print("\n------ B9 ------\n")
                                        

                                        print("\n------ B10 ------\n")

                                        #current_table_placeholder.empty()
                                        #select_sheet_ph.empty()
                                        
                                        #st.sidebar.empty()
                                        st.cache_data.clear()
                                        
                                        #current_sheet = None

                                        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

                                        print(dfs[0])
                                        print(st.session_state.file_path)


                                        #current_sheet = st.empty()
                                                
                                        #current_sheet = select_sheet_ph.radio("Select sheet",sheets)

                                        current_table_placeholder.dataframe(dfs[sheets.index(sheets[0])], height=500)
                                        cache_clear = True
        

else:
    st.session_state.file_path = None
    st.session_state.uploaded_file = None 


if st.session_state.dev_mode:
    if st.session_state.continue_clicked:
        text_chain_1.empty()
        with text_chain_2.chat_message("human"):    
                                        try:
                                            #code_editor.empty()
                                            st.write("\n\nInitiating code execution...")
                                            exec(st.session_state.user_input)
                                            status = save_sheets(st.session_state.file_path)
                                            st.caption("...Request executed")
                                            st.caption("-Reloading workbook-")
                                            time.sleep(0.5)
                                            message = {"role": "ai", "content": f"Successfully executed with: \n{st.session_state.user_input}"}
                                            print("\n------ B8 ------\n")
                                            #st.session_state.messages.append(message)
                                            

                                        except Exception as e:
                                            st.caption(f"Error: {e}")
                                            st.caption("Analysing the error....")
                                            print("Got error: ", e)

                                            new_code = refresh_code(st.session_state.request, e, st.session_state.file_path, st.session_state.user_input, st.session_state.additional)
                                            #st.code(f"New code: \n {new_code}")
                                            print("New code: ", new_code)

                                            try:
                                                st.caption("Initializing new refreshed code....")
                                                exec(new_code)
                                                status = save_sheets(st.session_state.file_path)
                                                st.write("Request Executed")
                                                message = {"role": "ai", "content": f"Successfully executed with: \n{str(st.session_state.user_input)}"}
                                                print("\n------ B8 ------\n")
                                                #st.session_state.messages.append(message)
                                                

                                            except Exception as e2:
                                                st.caption(f"New Error: {e2}")
                                                message = {"role": "ai", "content": f"Execution unsuccessful due to error: \n{e2}"}
                                                #st.session_state.messages.append(message)
                                                print("Got a new error: ", e2)
                                                print("\n------ B9 ------\n")
                                        

                                        print("\n------ B10 ------\n")
                                        msg_length_1 = len(st.session_state.messages)


                                        
                                        st.session_state.messages = [{"role": "ai", "content": "..."}]
                                        cache_clear = True
                                        st.session_state.request = None
                                        st.session_state.continue_clicked = False


                                   



# Post execution

if cache_clear:
        print("\n------ B10 ------\n")

        current_table_placeholder.empty()
        select_sheet_ph.empty()
        
        st.sidebar.empty()
        st.cache_data.clear()
        
        current_sheet = None

        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

        print(dfs[0])
        print(st.session_state.file_path)


        current_sheet = st.empty()
                
        current_sheet = select_sheet_ph.radio("Select sheet",sheets)

        current_table_placeholder.dataframe(dfs[sheets.index(current_sheet)], height=500)


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
            
            st.session_state.dev_mode = st.sidebar.toggle("Developer Mode")
            if st.session_state.dev_mode:
                st.sidebar.button("Abort Step", on_click=lambda: st.rerun())
                  


# C:/Users/Administrator/Documents/reporter
# C:/Users/Administrator/Documents/reporter
