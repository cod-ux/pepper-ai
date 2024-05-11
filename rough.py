import pandas as pd
from openpyxl import load_workbook

def excel_to_df(file_path):
    wb = load_workbook(filename=file_path, data_only=False)
    dfs = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        data = ws.values
        columns = next(data)
        data = list(data)
        dfs.append(pd.DataFrame(data, columns=columns))
    return dfs

# Example usage:
file_path = "sales_data_sample.xlsx"
dfs = excel_to_df(file_path)

print("No. of dfs: ", len(dfs))
for df in dfs:
    print("New one: ")
    print(df.head(3))
