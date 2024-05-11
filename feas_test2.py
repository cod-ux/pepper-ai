import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from st_aggrid import AgGrid, GridOptionsBuilder
import json
import xlwings as xl
import xlrd

import streamlit as st
import pandas as pd
import pygsheets
import shutil

# Source file
source = "/Users/suryaganesan/vscode/ml/projects/reporter/sales_data_copy.xlsx"

# Destination directory
move_location = "/Users/suryaganesan/library/containers/com.microsoft.excel/data/"

# Move the file
shutil.copy(source, move_location)

