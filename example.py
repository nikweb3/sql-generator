import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import os

root = tk.Tk()
is_key_var = tk.IntVar(value=-1)  # -1 indicates no selection

# Dictionary to map column names to their corresponding data types
column_data_types = {
    "int_column": "int",
    "decimal_column": "decimal",
    "float_column": "float",
    "varchar_column": "varchar(255)",  # You can specify the desired length (e.g., varchar(50))
    "datetime_column": "datetime"
}


def enable_file_uploader(*args):
    selected_format = e.get()
    if selected_format != "Choose Format":
        upload_button.config(state=tk.NORMAL)
    else:
        upload_button.config(state=tk.NORMAL)


def upload_file():
    file_type = e.get()
    file_type_dict = {
        "Excel": [("Excel files", "*.xlsx"), ("Excel files", "*.xls")],
        "CSV": [("CSV files", "*.csv")]
    }
    file = filedialog.askopenfilename(title="Select file", filetypes=file_type_dict.get(file_type, []))
    if file:
        if file_type == "Excel":
            df = pd.read_excel(file, header=None)
        elif file_type == "CSV":
            encodings_to_try = ['utf-8', 'ISO-8859-1', 'cp1252']
            df = None
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(file, header=None, encoding=encoding)
                    break  # Break out of the loop if successful
                except UnicodeDecodeError:
                    continue  # Try the next encoding if there's an error
            if df is None:
                # Handle the case where none of the encodings worked
                print("Failed to read CSV with any encoding")

        display_data(df)
        update_row_count_label(len(df))


def update_row_count_label(row_count):
    row_count_label.config(text=f"Total rows: {row_count}")


def update_headers():
    for i, entry in header_entries.items():
        if entry.winfo_exists():  # Check if the widget still exists
            tree.heading(i, text=entry.get())
        else:
            # Handle the case where the entry widget has been destroyed
            pass  # Add any cleanup or error handling as needed
    # Do not clear the header_entries dictionary here


def create_header_entries(df):
    for i, col in enumerate(df.columns):
        entry = ttk.Entry(header_frame, width=12)
        entry.insert(0, f"Column {i + 1}")
        entry.grid(row=0, column=i, padx=2, pady=2)
        header_entries[i] = entry


def add_new_column():
    create_header_entries(pd.DataFrame(columns=[*tree["columns"]]))
    new_col_name = new_col_name_entry.get()
    dummy_data = dummy_data_entry.get() if generate_dummy_var.get() else ""
    tree["columns"] = (*tree["columns"], new_col_name)
    tree.heading(new_col_name, text=new_col_name)
    tree.column(new_col_name, anchor="center", width=100)

    for item in tree.get_children():
        tree.set(item, new_col_name, dummy_data)


# Initialize Treeview with default columns
def initialize_treeview():
    tree["columns"] = ("Column1", "Column2")
    tree["show"] = "headings"
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)


def toggle_dummy_data_entry():
    if generate_dummy_var.get():
        dummy_data_entry.config(state=tk.NORMAL)
    else:
        dummy_data_entry.config(state=tk.DISABLED)


def clear_header_entries():
    for widget in header_frame.winfo_children():
        widget.destroy()


def clear_placeholder(event):
    entry = event.widget  # Get the widget that triggered the event
    placeholder_text = entry.placeholder_text  # Retrieve the stored placeholder text
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)


def add_placeholder(event):
    entry = event.widget  # Get the widget that triggered the event
    placeholder_text = entry.placeholder_text  # Retrieve the stored placeholder text
    if not entry.get():
        entry.insert(0, placeholder_text)


def display_data(df):
    clear_header_entries()
    create_header_entries(df)
    # Clear existing data in Treeview
    for i in tree.get_children():
        tree.delete(i)

    # Configure Treeview columns
    tree["columns"] = tuple(range(len(df.columns)))
    tree["show"] = "headings"
    for i in range(len(df.columns)):
        tree.heading(i, text=f"Column {i + 1}")
        tree.column(i, anchor="center", width=100)

    # Insert data
    for row in df.to_numpy().tolist():
        tree.insert("", "end", values=row)


def set_fullscreen():
    root.state("zoomed")


def setup_columns():
    # Shared variable for all 'IsKey?' radio buttons
    global is_key_var
    # Clear any existing widgets in the columns_frame
    for widget in columns_frame.winfo_children():
        widget.destroy()

    # Retrieve column headers from the treeview
    column_headers = [tree.heading(col)["text"] for col in tree["columns"]]

    # Get the first row of data to determine data types
    first_row = tree.item(tree.get_children()[0], 'values')

    # Loop through each column header and create entry widgets
    for i, col_header in enumerate(column_headers):
        # Entry for the column header
        col_header_entry = ttk.Entry(columns_frame)
        col_header_entry.insert(0, col_header)
        col_header_entry.grid(row=i, column=0, padx=5, pady=2, sticky="ew")

        # Determine the data type based on the content of the first row
        data_type = determine_data_type(first_row[i])

        # Entry for the data type with determined type
        data_type_entry = ttk.Entry(columns_frame)
        data_type_entry.insert(0, data_type)
        data_type_entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")

        # Radio buttons for 'IsKey?'
        # Radio button for 'IsKey?' - Yes
        is_key_yes = ttk.Radiobutton(columns_frame, text="Yes", variable=is_key_var, value=i)
        is_key_yes.grid(row=i, column=2, padx=5, pady=2, sticky="w")

        # Radio button for 'IsKey?' - No
        is_key_no = ttk.Radiobutton(columns_frame, text="No", variable=is_key_var, value=-1)
        is_key_no.grid(row=i, column=3, padx=5, pady=2, sticky="w")

        # Set default to 'No' for each row
        if is_key_var.get() != i:
            is_key_no.invoke()

            # Button that can only be pressed if a key column is selected
            submit_button = ttk.Button(columns_frame, text="Submit", state=tk.DISABLED, style='Accent.TButton',
                                       command=submit_columns)
            submit_button.grid(row=len(column_headers) + 1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

            # Function to update the state of the submit button based on radio button selection
            def update_submit_button(*args):
                submit_button.state(["!disabled"] if is_key_var.get() != -1 else ["disabled"])

            # Attach the update function to the shared IntVar
            is_key_var.trace_add("write", update_submit_button)


def submit_columns():
    # Assuming construct_create_table_statement() and construct_insert_statements()
    # are defined elsewhere and return respective SQL command strings.

    # Construct the 'CREATE DATABASE' SQL statement
    db_name = db_name_entry.get().strip()
    create_db_sql = f"CREATE DATABASE {db_name};\nUSE {db_name};\n"

    # Construct the 'CREATE TABLE' and 'INSERT' SQL statements
    create_table_sql = construct_create_table_statement()
    insert_sql = construct_insert_statements()

    # Combine all SQL statements
    full_sql_script = create_db_sql + create_table_sql + insert_sql

    # Define the file name
    table_name = table_name_entry.get().strip()
    filename = f"{table_name}-{db_name}-script.sql"

    # Prompt user to select directory and save the file
    selected_directory = filedialog.askdirectory(title="Select a folder to save the SQL file")

    if selected_directory:  # Check if a directory was selected
        full_path = os.path.join(selected_directory, filename)

        # Save to a file with utf-8 encoding using a context manager
        with open(full_path, "w", encoding='utf-8') as file:
            file.write(full_sql_script)

        print("SQL file created:", full_path)
    else:
        print("No directory selected. File not saved.")


def construct_create_table_statement():
    table_name = table_name_entry.get().strip()
    db_name = db_name_entry.get().strip()
    column_definitions = []
    primary_key = None

    # Adjust the index to correctly identify the Entry widgets
    entry_widgets = [w for w in columns_frame.winfo_children() if isinstance(w, ttk.Entry)]
    for i in range(0, len(entry_widgets), 2):  # Step by 2 as you have two entries per column (name and data type)
        column_name = entry_widgets[i].get().strip()
        data_type = entry_widgets[i + 1].get().strip()

        if not column_name or not data_type:
            continue

        column_definition = f"{column_name} {data_type}"
        column_definitions.append(column_definition)

        # Check if this is the primary key
        if is_key_var.get() == i // 2:
            primary_key = column_name

    sql_statement = f"CREATE TABLE {table_name} (\n"
    sql_statement += ",\n".join(column_definitions)
    if primary_key:
        sql_statement += f",\nPRIMARY KEY ({primary_key})"
    sql_statement += "\n);\n\n"

    return sql_statement


def construct_insert_statements():
    table_name = table_name_entry.get().strip()
    db_name = db_name_entry.get().strip()
    insert_statements = ""

    # Retrieve column data types
    column_data_types = [w.get().strip().lower() for w in columns_frame.winfo_children() if isinstance(w, ttk.Entry)][
                        1::2]  # Skip column names, only get data types

    for child in tree.get_children():
        row_data = tree.item(child, 'values')
        formatted_row_data = []

        for i, value in enumerate(row_data):
            # Check if the column data type is int or numeric and format accordingly
            if i < len(column_data_types) and (column_data_types[i] in ['int', 'numeric']):
                try:
                    # Try to convert to int and append without quotes
                    formatted_row_data.append(str(int(value)))
                except ValueError:
                    # Handle cases where conversion to int fails
                    formatted_row_data.append('NULL')  # Or handle it as you see fit
            else:
                # For other data types, append the value with quotes
                formatted_row_data.append(f"'{value}'")

        column_values = ', '.join(formatted_row_data)
        insert_statements += f"INSERT INTO {table_name} VALUES ({column_values});\n"

    return insert_statements


def determine_data_type(value):
    # Function to determine data type based on the content of a value
    try:
        # Try to convert to int
        int(value)
        return "int"
    except ValueError:
        try:
            # Try to convert to decimal (10,2)
            float_value = float(value)
            if float_value.is_integer():
                return "decimal(10,0)"
            else:
                return "decimal(10,2)"
        except ValueError:
            # If not a number, treat it as varchar(255)
            return "varchar(255)"


root.title("Nik's SQL Generator")
root.option_add("*tearOff", False)  # This is always a good idea

# Make the app responsive
root.columnconfigure(index=0, weight=1)
root.columnconfigure(index=1, weight=1)
root.columnconfigure(index=2, weight=1)
root.rowconfigure(index=0, weight=1)
root.rowconfigure(index=1, weight=1)
root.rowconfigure(index=2, weight=1)

# Create a style
style = ttk.Style(root)
# Import the tcl file
root.tk.call("source", "forest-dark.tcl")

# Set the theme with the theme_use method
style.theme_use("forest-dark")

# Create lists for the Comboboxes
option_menu_list = ["", "Choose Format", "Excel", "CSV", "JSON", "YAML"]

# Create control variables
e = tk.StringVar(value=option_menu_list[1])
e.trace_add("write", enable_file_uploader)

# Create main frames for each section with fixed 50% width
left_frame = ttk.Frame(root, padding=10)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.columnconfigure(0, weight=1)
left_frame.rowconfigure(0, weight=1)

right_frame = ttk.Frame(root, padding=10)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(0, weight=1)

# Create Label Frames for each section
document_upload_frame = ttk.LabelFrame(left_frame, text="Document Upload", padding=10)
document_upload_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
document_upload_frame.columnconfigure(0, weight=1)
document_upload_frame.rowconfigure(0, weight=1)

num_rows = 4  # Adjust this based on how many rows you are using
for i in range(num_rows):
    document_upload_frame.rowconfigure(i, weight=0)

# Label for displaying total row count
row_count_label = ttk.Label(document_upload_frame, text="Total rows: 0")
row_count_label.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

sql_generation_frame = ttk.LabelFrame(right_frame, text="SQL Generation", padding=10, width=900)
sql_generation_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
sql_generation_frame.columnconfigure(0, weight=1)

# Configure rows within sql_generation_frame
# Set weight to 0 for rows that should not expand
num_rows = 4  # Adjust this based on how many rows you are using
for i in range(num_rows):
    sql_generation_frame.rowconfigure(i, weight=0)

spacer_frame = ttk.Frame(sql_generation_frame, width=500, height=1)
spacer_frame.grid(row=num_rows, column=0, sticky="we")

# Set a specific width for the OptionMenu
optionmenu_width = max(map(len, option_menu_list)) + 5  # Extra space for aesthetics
optionmenu = ttk.OptionMenu(document_upload_frame, e, *option_menu_list)
optionmenu.config(width=optionmenu_width)
optionmenu.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

# Create an 'Upload File' button
upload_button = ttk.Button(document_upload_frame, text="Upload File", state=tk.NORMAL, command=upload_file)
upload_button.grid(row=0, column=1, padx=10, pady=0, sticky="ew")

# Sizegrip
sizegrip = ttk.Sizegrip(root)
sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

# Set the application to full screen
set_fullscreen()

# Center the window, and set minsize
root.update()
x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

# Frame for Treeview and scrollbar
tree_frame = ttk.Frame(document_upload_frame)
tree_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
tree_frame.rowconfigure(0, weight=1)
tree_frame.columnconfigure(0, weight=1)

# Treeview
tree = ttk.Treeview(tree_frame)
tree.grid(row=0, column=0, sticky="nsew")

# Scrollbars for Treeview
h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
h_scroll.grid(row=1, column=0, sticky="ew")
tree.configure(xscrollcommand=h_scroll.set)

v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
v_scroll.grid(row=0, column=1, sticky="ns")
tree.configure(yscrollcommand=v_scroll.set)

# Set the size of the Treeview frame
tree_frame.grid_propagate(False)
tree_frame.config(width=600, height=250)

# Frame for updating column headers
update_header_frame = ttk.LabelFrame(document_upload_frame, text="Update Column Headers", padding=(20, 10))
update_header_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

# Frame for header entries inside the update_header_frame
header_frame = ttk.Frame(update_header_frame)
header_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Button to update column headers inside the update_header_frame
update_headers_button = ttk.Button(update_header_frame, text="Update Headers", command=update_headers)
update_headers_button.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")

header_entries = {}  # Dictionary to store header entry widgets

# Frame for adding new column with header
add_col_frame = ttk.LabelFrame(document_upload_frame, text="Add New Column", padding=(20, 10))
add_col_frame.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

# New column name entry with placeholder text
new_col_name_entry = ttk.Entry(add_col_frame)
new_col_name_entry.insert(0, "Enter Column Name")
# Example usage for new_col_name_entry
new_col_name_entry.bind("<FocusIn>", clear_placeholder)
new_col_name_entry.bind("<FocusOut>", add_placeholder)
new_col_name_entry.grid(row=0, column=0, padx=5, pady=5)

# Checkbutton for generating dummy data
generate_dummy_var = tk.BooleanVar()
generate_dummy_check = ttk.Checkbutton(add_col_frame, text="Generate dummy data", variable=generate_dummy_var,
                                       command=toggle_dummy_data_entry)
generate_dummy_check.grid(row=0, column=1, padx=5, pady=5)

# Entry for dummy data
dummy_data_entry = ttk.Entry(add_col_frame, state=tk.DISABLED)
dummy_data_entry.grid(row=0, column=2, padx=5, pady=5)

# Button to add new column
add_col_button = ttk.Button(add_col_frame, text="Add Column", command=add_new_column)
add_col_button.grid(row=0, column=3, padx=5, pady=5)

# Add widgets to sql_generation_frame
# Label and entry for Table Name
table_name_label = ttk.Label(sql_generation_frame, text="Table Name:")
table_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
table_name_entry = ttk.Entry(sql_generation_frame)
table_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Label and entry for Database Name
db_name_label = ttk.Label(sql_generation_frame, text="Database Name:")
db_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
db_name_entry = ttk.Entry(sql_generation_frame)
db_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Button to setup columns
setup_columns_button = ttk.Button(sql_generation_frame, text="Setup Columns", command=setup_columns)
setup_columns_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Frame to hold the column name and data type entries
columns_frame = ttk.Frame(sql_generation_frame, padding=(20, 10))
columns_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")
columns_frame.columnconfigure(1, weight=1)  # Give more weight to the data type column

# Start the main loop
root.mainloop()
