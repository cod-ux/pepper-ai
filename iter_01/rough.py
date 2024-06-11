from code_agents_01 import generate_code, create_plan


request = "Create a new column that can be used as a Unique ID with four digit numbers"
source = "/Github/reporter/excel_source/sales_data_copy.xlsx"
additional = create_plan(source=source, request=request)

print(f"Requirements:\n{additional.content}")

code = generate_code(request=request, additional=additional, source=source)

print(f"Code:\n{code}")