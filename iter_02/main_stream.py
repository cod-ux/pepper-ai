import streamlit as st
import asyncio
import os
import pandas as pd
from temp_manipulate import format_request
from graph_manipulate import manipulate
from graph_explore import explore
from streamlit_utils_02 import copy_excel_locally, save_sheets, handle_duplicate_columns, unmerge_sheets, get_binary, undo, load_sheets_to_dfs


st.set_page_config(layout="wide")
# initializing session variables

if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "system", "content": "hello, what can i do for you today?"}]

if 'exec_steps' not in st.session_state:
    st.session_state.exec_steps = []

if "file_path" not in st.session_state:
   st.session_state.file_path = None

if "uploaded_file" not in st.session_state.keys():
    st.session_state.uploaded_file = None

if "cache_clear" not in st.session_state:
    st.session_state.cache_clear = False

if "state_stack" not in st.session_state:
    st.session_state.state_stack = [] # binaries of excels


# Pre-upload

header_ph = st.empty()
header_ph.markdown( "<h3 style='text-align: center;'>Pepper, The Data Co-pilot</h3>", unsafe_allow_html=True)
st.markdown( "<h6 style='text-align: center;'>Automate repeatitive data tasks by coding in natural language</h6>", unsafe_allow_html=True)
st.markdown("<h4> </h4>", unsafe_allow_html=True)
uploader_ph = st.empty()
cache_clear = False
img_folder = "/Users/suryaganesan/Documents/GitHub/reporter/ph_images"

uploaded_file = st.file_uploader("Upload or Select Excel file", ["xlsx", "xls"])


# Post-upload

    
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

    if st.session_state.file_path is not None:
            st.markdown("<h4 style='text-align: center;'></h4>", unsafe_allow_html=True)
            print("\n------ B4 ------\n")
            print(f"Uploaded file says: {st.session_state.uploaded_file}")
            print(f"File path says: {st.session_state.file_path}")

            st.sidebar.title("Side Panel")
            
            st.markdown(f"<h5>{st.session_state.uploaded_file.name}: </h5>", unsafe_allow_html=True)
                
            
            dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

            sidebar_ph = st.sidebar.empty()
            current_table_placeholder = st.empty()

            current_table_placeholder.empty()
            sidebar_ph.empty()


            current_sheet = st.empty()
            
            with sidebar_ph.container():
                current_sheet = st.radio("Select sheets", sheets)
                mode = st.selectbox("Mode", ["Explore", "Manipulate"], )

            current_table_placeholder.dataframe(dfs[sheets.index(current_sheet)], height=500)

    #     Chat box
            request = st.chat_input("code in natural language...")


            if request:
                    print("\n------ B5 ------\n")
                    st.session_state.messages.append({"role": "human", "content": request})
                    with st.chat_message("human"):
                            st.write(request)

#     Command execution

            if st.session_state.messages[-1]["role"] != "ai":
                print("\n------ B6 ------\n")
                if request:



                    if request != "quit":
                            print("\n------ B7 ------\n")
                            st.session_state.state_stack.append(get_binary(st.session_state.file_path))
                            test = save_sheets(st.session_state.file_path)

                    if mode == "Explore":
                        if request != 'quit':
                            code_solution = ''
                            formatted_req = format_request(request, st.session_state.file_path)
                            temp = []



                            inputs = {"messages": [('user', formatted_req)], "request": request, "source_path": st.session_state.file_path, "max_iterations": 3, "iterations": 0, "past_execs": st.session_state.exec_steps, "response": "", "current_task": ""}
                            response = ''
                            for events in explore.stream(inputs):
                                for key, value in events.items():
                                    if key != "__END__":
                                        try:
                                            current_task = value["current_task"]
                                            streaming = st.empty()
                                            if current_task == "Closing...":
                                                response = value["response"]
                                                streaming.empty()
                                                streaming.write(response)
                                                code_solution = value["response"]
                                            elif current_task == "Plan completed...":
                                                response = value["current_task"]
                                                streaming.empty()
                                                streaming.caption(response)
                                                streaming.caption("Generating code...")
                                            else:
                                                response = value["current_task"]
                                                streaming.empty()
                                                streaming.caption(response)
                                            
                                        except Exception as e:
                                            print(f"Error Streaming event: {e}")

                            imgs = os.listdir(img_folder)
                            for img in imgs:
                                img = os.path.join(img_folder, img)
                                st.image(img)
                            st.session_state.messages.append({"role": "ai", "content": "Program executed"})
                            st.session_state.exec_steps.append({"question": request, "answer": code_solution})
                            cache_clear = True


                    if mode == "Manipulate":
                        if request != 'quit':
                            reply = ''
                            formatted_req = format_request(request, st.session_state.file_path)
                            temp = []



                            inputs = {"messages": [('user', formatted_req)], "request": request, "source_path": st.session_state.file_path, "max_iterations": 3, "iterations": 0, "past_execs": st.session_state.exec_steps, "response": "", "current_task": ""}
                            response = ''
                            for events in manipulate.stream(inputs):
                                for key, value in events.items():
                                    if key != "__END__":
                                        try:
                                            current_task = value["current_task"]
                                            streaming = st.empty()
                                            if current_task == "Closing...":
                                                response = value["response"]
                                                with streaming.container():
                                                    st.write(response)
                                                reply = value["response"]
                                            elif current_task == "Plan completed...":
                                                response = value["current_task"]
                                                streaming.empty()
                                                st.caption(response)
                                                st.caption("Generating code...")
                                            else:
                                                response = value["current_task"]
                                                streaming.empty()
                                                st.caption(response)
                                            
                                        except Exception as e:
                                            print(f"Error Streaming event: {e}")

                            st.session_state.messages.append({"role": "ai", "content": "Program executed"})
                            st.session_state.exec_steps.append({"question": request, "answer": reply})
                            cache_clear = True


else:
    st.session_state.file_path = None
    st.session_state.uploaded_file = None
# Post execution

if cache_clear:
        print("\n------ B10 ------\n")
        
        st.sidebar.empty()
        st.cache_data.clear()
        #current_sheet = None

        dfs, sheets = load_sheets_to_dfs(st.session_state.file_path)

        print(dfs[0])
        print(st.session_state.file_path)

        current_table_placeholder.empty()
        #sidebar_ph.empty()


        #current_sheet = st.empty()
                
        #with st.sidebar.container():
        #    current_sheet = st.radio("Select sheet", sheets)
        #    mode = st.selectbox("mode", ["Explore", "Manipulate"])

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
                  

