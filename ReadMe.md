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

## Tracking

Exp 1: Add the entire prompt to one message

Result: Did not work, still made a multi-step plan for a simple request

Exp 2: Change the propmt to identify tasks instead of make a plan.

Result: Tasks are more accurate and works.
Challenge: Individual tasks are some time exploratory and provide some answers for the next step to use, 
but since the generated code is dynamically executed, there isn't a way to add the exploration script's response to the messages.

Exp 3: Ask the generated code to always return a response with the same variable name to extract and add to messages if the response is not None.
Implementation: 
1. Planner needs to run on messages not template, and messages variable should be used from state class. (done)
2. Generated code should be asked to: Save file with the same source file_name and return a response variable with the same name.
3. Response needs to be added to messages by checking if there is a response every time code is executed

Challenge in 3-1: planner template encounters some error when loading template from {template function}
Solution: Creating a planner object from llms newly every time planner node is called. Need to check if this is time consuming.

Challenge 3-2: First loop runs well, but adding to the messages seems to pop an error when the second loop starts.
Solution: Needed to create the code gen chain only once and not multiple times

Challenge 3-3: We want the user request to be correctly executed in the final step. To do that we were thinking of
breaking the request to list of tasks, then execute each task individually. Hoping that executing step by step would result in
minimal errors. But this requires viewing the new state of the excel after each step. Instead would be accurate if we just, iteratively
add code adn executing only in the end?
Trial solution: At each task take the code solution so far, mentioning the tasks it achieves and provide a new task to add to the
existing code. And when there is no more tasks left to complete, execute the code.

Rewriting Exp 3: Make the flow such that at each step code is added iteratively to each task and executed at the end when the
list is exhausted.

Implementation: 
1. No change to planner (done)
2. Stop messages from adding sheet views at every step. (done)
3. First message after planning should be include list of tasks. (done)
4. Need to maintain a variable for past_code_steps. (done)
5. After exec each task, add message to say here are the steps coded. (done)
6. Before exec each task, Add here is the task that needs to be added to the code. (done)

7. Ask the code to return a response object with the same variable name in the end, to check if the function was executed successfully or what the error was.
But would that be necessary? What if we just executed and figured what the mistake was ourselves? This would probably help debugging a lot.
But still, I'll have to ask the LLM to include try statements everywhere and ask it to write and return code that is easily debuggable.
But again, I can still ask it to write debuggable code with a lot of try statements, so that the error can be specified.
Preferably for simplicity, we do not include try statements inside and catch adn use the error only when we execute the code.
The alternative would be to ask the LLM return a response object, describing the problem when an expected error is thrown. 
Which will be used for debugging the code better.
We're gonna choose simple and just use the error that may be caught during dynamic execution itself. Cuz the alternative is a lot of work and complexity.
Cancelled step 7.

Solution: Created an iterative coding process where an additional task is completed at each step to produce the final code
that achieves all tasks.

Exp 4: Add a try statement to execute the imports and code blocks. And the functionality to restart the generation process
one additional time to correct the error.

Implementation:
1. Add try statements and returning the error to the state variable error. (done)
2. Add error variable to messages if caught. (done)

Exp 5: Figure out how to charge users

Challenge: Can't accept payments to my name or account as I'm on a student visa
Trial Solution: Create a paypal business account for an Indivual business owner in India and work for them to promote their business.
Not going to get IEC code because I'm only allowing pre-order and free trial and charging a one-time fee of £0.

Exp 6: Make the Graph to add nodes - plan, generate, check & reflect, should end.

Implementation:
(Make a graph first)
1. Add check code to graph. (done)
2. Add should end to graph. (done)
3. Add reflect to graph. (done)
4. Make responses print asynchronously. (done)
5. Maintain steps executed so far + code solutions.(done)
6. Make a quick CLI to test the graph app against differet requests (D2)
7. Include past 5 executed requests + code solutions from streamlit's session state when making future plans for requests. (D2)
8. Make generation messages short term, remove them after final script is generated. (done)
9. Make a Langgraph app to explore and answer questions about a dataset. (D3) - Ask the LLM to use st.write for texts and images.

10. Use Langgraph app to generate scripts. (D4)
11. Stream Langgraph sys messages to streamlit. (D4)
12. Make RAG bot for documentation. (D4)

