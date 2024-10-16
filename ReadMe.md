# Pepper AI: Spend Less Time Preparing Your Data for Analysis

**Pepper AI** is a web app designed to streamline your data preparation process. Upload an Excel file, and with the help of AI-powered chat commands, explore and manipulate your data to get it analysis-ready quickly and efficiently.

## Key Features

- Upload Excel files and interact with them through a chat-based interface.
- Explore and manipulate datasets with ease.
- Undo changes and export the cleaned and manipulated file in just a click.
- Utilize two intent modes:
  - **Explore**: Ask questions like "Show rows with empty values" to analyze the data.
  - **Manipulate**: Issue commands like "Delete the last column" to modify your dataset.

## User Flow

1. **Upload File**: Drop an Excel file into the app for analysis.
2. **Table View**: The first sheet appears in a table view. The sidebar shows available sheets to select from.
3. **Intent Modes**: 
   - **Explore** mode lets users ask questions about their data.
   - **Manipulate** mode enables users to issue commands to transform the dataset.
4. **Undo**: Users can undo changes using the undo button.
5. **Export**: Download the modified Excel file with the export button.

## Solution Architecture

- **Streamlit**: Used for creating the single-page UI prototype.
- **Langgraph**: Manages agents that "explore" and "manipulate" the data.
- **Xlwings**: Handles Excel file operations, such as opening and saving, including formula calculations.
- **Pandas**: Processes and displays data from Excel sheets.
