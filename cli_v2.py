import os
import click
import xlwings as xw

from utils import load_sheets_to_dfs

from code_agents import (
    create_plan,
    generate_code,
    review_code,
    refresh_code
)

from phoenix.trace.openai import OpenAIInstrumentor
import phoenix as px


# Section 1: Choose source file and verify

def list_open_excel_files():
    app = xw.apps.active
    click.echo("-------------------------------------")
    if app:
        click.echo("\nExcel is currently open.\n")
        workbooks = app.books
        click.echo("List of Open workbooks:")

        if workbooks:
            for i, wb in enumerate(workbooks, start=1):
                click.echo(f"{i}. {wb.name}")
            click.echo("\n")
        else:
            click.echo("(None)\n")
        click.echo("-------------------------------------")

    else:
        click.echo("Excel is not currently open.\n")

def copy_excel_file(source_path, destination_folder):
    try:
        if not os.path.exists(destination_folder):
            click.echo(f"Couldn't find the Microsoft container folder to perform operations: {destination_folder}\n")
            return None

        filename, ext = os.path.splitext(os.path.basename(source_path))
        destination_filename = f"{filename}_copy{ext}"
        destination_filepath = os.path.join(destination_folder, destination_filename)

        if os.path.exists(destination_filepath):
            click.echo(f"There is an old copy of the file that already exists in the microsoft container: {destination_filepath}\n")
            os.remove(destination_filepath)

        os.system(f'cp "{source_path}" "{destination_filepath}"')
        click.echo(f"File copied to: {destination_filepath}\n")
        return destination_filepath
    
    except Exception as e:
        click.echo(f"Error copying file: {e}\n")
        return None

def open_excel_file(file_path):
    try:
        app = xw.App(visible=True)
        wb = app.books.open(file_path)
        return app, wb
    except Exception as e:
        click.echo(f"Error opening file: {e}\n")
        return None, None

def close_excel_file(wb):
    try:
        if wb:
            wb.close()
    except Exception as e:
        click.echo(f"Error closing Excel: {e}\n")

# Pseudo code for handling natural language commands
def handle_commands(wb):
        command = click.prompt("Enter your command: ")
        if command.lower() == "exit" or "close":
            close_excel_file(wb)
            return True

        elif command.lower() == "save":
            wb.save()
            click.echo("File saved.")
            return False

        elif command.lower() == "undo":
            wb.api.Application.SendKeys("^z")
            click.echo("Undo completed.")
            return False

        else:
            click.echo("Command not recognized")
            return False

@click.command()
def main():
    while True:
        list_open_excel_files()
        file_name = click.prompt("Enter the name of the Excel file you want to operate (or enter nothing to refresh the list): ", default="")
        click.echo("\n")
        if file_name.lower() == "":
            continue
        else:
            app, wb = None, None
            for workbook in xw.apps.active.books:
                if file_name.lower() == workbook.name.lower():
                    source_file = workbook.fullname
                    break
                    
            else:
                click.echo("Invalid file name. Please enter a valid file name from the list.")
                continue

            destination_folder = f"/Users/{os.getenv('USER')}/Library/Containers/com.microsoft.excel/Data"
            copied_file_path = copy_excel_file(source_file, destination_folder)
            if copied_file_path:
                app, wb = open_excel_file(copied_file_path)
                

        if True:
            # Perform operations on the workbook
            the_end = False
            while not the_end:
                the_end = handle_commands(wb)

            app.quit()
            break

if __name__ == "__main__":
    main()
