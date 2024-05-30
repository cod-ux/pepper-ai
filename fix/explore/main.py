# Fix format request
import pandas as pd
from temp_explore import format_request


source = '/Users/suryaganesan/vscode/ml/projects/reporter/excel_source/sales_data_copy.xlsx'
state = {"request": "Make me a graph", "source": source}

formatted = format_request(state["request"], state["source"])

print("Formatted request: \n", formatted)

"""
Ideal prompt:

### PREVIOUS CONVERSATION
### QUERY
 What is this data about?
### ANSWER
 The data consists of information related to orders, including order details like order number, quant ...
### QUERY
 Delete the last column and save it as an excel
### QUERY
 How many integer columns do we have in this?
### QUERY
 Make a plot with this data
### QUERY
 Make any chart
<dataframe>
dfs[0]:10406x22
ORDERNUMBER,QUANTITYORDERED,DEALSIZE,ORDERLINENUMBER,SALES,ORDERDATE,STATUS,QTR_ID,MONTH_ID,YEAR_ID,PRODUCTLINE,MSRP,PRODUCTCODE,CUSTOMERNAME,PHONE,ADDRESSLINE1,ADDRESSLINE2,CITY,STATE,POSTALCODE,COUNTRY,TERRITORY
10145.0,35.0,,,5756.52,,In Process,QTR_ID,,,Classic Cars,118,,"Dragon Souveniers, Ltd.",0033383230,11328 Douglas Av.,,Newark,,50553,Japan,
,20.0,Small,11.0,,4/8/2005 0:00,,,10.0,2003,,MSRP,PRODUCTCODE,Gift Depot Inc.,6698603660,,Level 15,Torino,Osaka,44000,UK,Japan
10126.0,,Large,12.0,4860.24,11/6/2003 0:00,Disputed,2,7.0,YEAR_ID,PRODUCTLINE,,S10_4698,,2089168840,9408 Furth Circle,ADDRESSLINE2,,Tokyo,,,TERRITORY
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }

```



### QUERY
 How many entries do we have?

Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.

If you are asked to plot a chart, use "matplotlib" for charts, save as png at 'exports' folder as temp_chart.png.


Generate python code and return full updated code:

"""