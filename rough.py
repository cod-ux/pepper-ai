import os
import time
import xlwings as xw
from openpyxl import load_workbook

def open_excel_file(file_path):
    try:
        app = xw.App(visible=True)
        wb = app.books.open(file_path)
        return app, wb
    except Exception as e:
        print(f"Error opening file: {e}")
        return None, None

def close_excel_file(wb):
    try:
        if wb:
            wb.close()
    except Exception as e:
        print(f"Error closing Excel: {e}")

def main():
    file_name = "save.xlsx"
    file_path = os.path.abspath(file_name)
    app, wb = open_excel_file(file_path)
    
    if app and wb:
        # Load workbook using openpyxl
        wb_openpyxl = load_workbook(file_path)
        ws = wb_openpyxl.active
        
        # Change the value of cell A2 to "Changed"
        ws['A2'] = "Changed"
        
        # Wait for 6 seconds
        time.sleep(6)
        
        # Save and close the workbook using openpyxl
        try:
            wb_openpyxl.save(file_path)
            print("File saved.")
        except Exception as e:
            print(f"Error while saving: {e}")
        
        # Close the openpyxl workbook
        wb_openpyxl.close()
        
        # Keep the xlwings workbook open
        input("Press Enter to close the Excel file...")
        close_excel_file(wb)
        app.quit()

if __name__ == "__main__":
    main()
