def main():

    with uploader_ph.container():
       uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    while uploaded_file is None:
        pass

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
                    print("Creating a plan...\n")
                    plan = create_plan(request, file_path)

                    st.write(f"The plan: \n{plan}")
                    print("The plan: \n", plan)

                    st.write("Generating script")
                    script_generated = generate_code(request, file_path, plan)

                    st.code(f"Code generated: \n {script_generated}")
                    print("The code: \n", script_generated)
                    print("\n\nReviewing code...")

                    reviewed_script = review_code(request, script_generated, file_path, plan)

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
                        st.session_state.cache_clear = True

                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.write("Analysing the error....")
                        print("Got error: ", e)

                        new_code = refresh_code(request, e, file_path, plan, final_script)
                        st.code(f"New code: \n {new_code}")
                        print("New code: ", new_code)

                        try:
                            st.write("Initializing new refreshed code....")
                            exec(new_code)
                            status = save_sheets(st.session_state.file_path)
                            st.write(f"Saving changes: {status}")
                            message = {"role": "ai", "content": f"{final_script}"}
                            st.session_state.messages.append(message)
                            st.session_state.cache_clear = True

                        except Exception as e2:
                            st.write(f"New Error: {e2}")
                            print("Got a new error: ", e2)

    if st.session_state.cache_clear:
        st.cache_data.clear()
        st.write("Cache data should be cleared")

        file_path = st.session_state.file_path

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

        st.session_state.cache_clear = False
