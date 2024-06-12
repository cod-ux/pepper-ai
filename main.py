import pandas as pd

from graph_explore import explore
from temp_explore import (
    planner_template,
    format_request,
    code_chain_template,
    data_analyst_template
)


source = 'C:/Users/Administrator/Documents/github/reporter/excel_source/sales_data_copy.xlsx'


def main():
    df = pd.read_excel(source)
    print(df.head(7))
    executions = []
    while True:
        req = input(">> ")
        formatted_req = format_request(req, source)
        temp = []

        inputs = {"messages": [('user', formatted_req)], "request": req, "source_path": source, "max_iterations": 3, "iterations": 0, "past_execs": executions, "response": ""}
        msg = explore.invoke(inputs)



if __name__ == "__main__":
    main()