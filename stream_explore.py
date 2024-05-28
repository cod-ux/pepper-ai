import streamlit as st
import asyncio
import os
import pandas as pd
from temp_explore import format_request
from graph_explore import explore

source = '/Users/suryaganesan/vscode/ml/projects/reporter/pivot.xlsx'

if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "ai", 
        "content": "Hello, operator. What can I do for you today?",
    }]

if 'exec_steps' not in st.session_state:
    st.session_state.exec_steps = []

request = st.chat_input("Enter your question...")
img_folder = "/Users/suryaganesan/vscode/ml/projects/reporter/ph_images"
            
if request:
    print("\n------ B5 ------\n")
    for img in os.listdir(img_folder):
        img = os.path.join(img_folder, img)
        os.remove(img)
    
    st.session_state.messages.append({"role": "human", "content": request})
    with st.chat_message("human"):
        st.write(request)

#     Command execution

    if st.session_state.messages[-1]["role"] != "ai":
        print("\n------ B6 ------\n")
        if request:
            with st.chat_message("ai"):
                if request != "quit":
                    code_solution = ''
                    formatted_req = format_request(request, source)
                    temp = []



                    inputs = {"messages": [('user', formatted_req)], "request": request, "source_path": source, "max_iterations": 3, "iterations": 0, "past_execs": st.session_state.exec_steps, "response": "", "current_task": ""}
                    response = ''
                    for events in explore.stream(inputs):
                        for key, value in events.items():
                            if key != "__END__":
                                try:
                                    current_task = value["current_task"]
                                    streaming = st.empty()
                                    if current_task == "Closing...":
                                        response = value["response"]
                                        with streaming.container():
                                            st.write(response)
                                        code_solution = value["response"]
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

                    imgs = os.listdir(img_folder)
                    for img in imgs:
                        img = os.path.join(img_folder, img)
                        st.image(img)
                    st.session_state.messages.append({"role": "ai", "content": "Program executed"})
                    st.session_state.exec_steps.append({"question": request, "answer": code_solution})