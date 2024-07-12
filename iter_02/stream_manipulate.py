import streamlit as st
import asyncio
import os
import pandas as pd
from temp_manipulate import format_request
from graph_manipulate import manipulate

source = 'C:/Users/Administrator/Documents/reporter/excel_source/sales_data_copy.xlsx'

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
                    reply = ''
                    formatted_req = format_request(request, source)
                    temp = []



                    inputs = {"messages": [('user', formatted_req)], "request": request, "source_path": source, "max_iterations": 3, "iterations": 0, "past_execs": st.session_state.exec_steps, "response": "", "current_task": ""}
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
                    st.session_state.exec_steps.append({"request": request, "update": reply})