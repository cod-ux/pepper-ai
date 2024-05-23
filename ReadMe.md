# Command AI: Spend less time preparing your data for analysis

A web app to clean & prepare your excel data for analysis faster by manipulating it with chat commands

## Userflow
1. User drops in one excel file for analysis
2. The first sheet is shown in table view and the available list of sheets to choose is shown in the sidebar
3. The user chooses between two intent modes: "Explore" and "Manipulate", based on if they want to explore the dataset or manipulate it
4. For explore, the user posts questions like "Show the list of rows that have empty values". Results are outputed in the chatbox.
5. For manipulate, the user posts commands to change the source excel file to prepare it for analysis.
6. The user can undo any changes, with the undo button on the top left.
7. The user can also download the manipulated excel file through the export button on the top right.

## Solution Architecture
1. Streamlit - To create the UI of the single page application (prototype).
2. Langgraph - To create a graph with agents to "explore" and "Manipulate" the excel data
3. Xlwings - To load and save excel files by opening the app to calculate formulas to get the data.
4. Pandas - To convert and display sheets.

## So far
1. Built UI to display table and sheets, enter chat commands
2. Code agents to plan and review code to execute user commands.

## Coding Plan
1. Add unmerge functionality before laoding. (d)
2. Add undo button & functionality, by maintaining list of states as binary files in main page code. (d)
3. Add export button + save button functionality + record chat messages. (d)
4. Add LLM agents to 'explore' datasets without UI.
5. Create planning graph, code generation graph for manipulate.
6. Create planning graph, code generation graph for explore.
7. Figure everything out with streamlit UI after backend work is complete 100%.

## Goals list
1. Fully functional app with explore & manipulate with LLM agents only without UI.
2. Fully functional app with Langgraph implementation for cycles without UI.
3. Fully functional app with chain-of-thought past iteration history without UI.
4. Fully functional app with UI.

## Next steps
1. Make plan step decide if execution should be multi-step and provide list of steps to execute.
2. Make plan and generate code and execute each step.
3. Make plan, execute each step, fix errors and replan to achieve goal, with graph.