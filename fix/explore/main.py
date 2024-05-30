# Fix format request
import pandas as pd
from temp_explore import format_request


source = '/Users/suryaganesan/vscode/ml/projects/reporter/excel_source/sales_data_copy.xlsx'
state = {"request": "Make me a graph", "source": source}

formatted = format_request(state["request"], state["source"])

print("Formatted request: \n", formatted)