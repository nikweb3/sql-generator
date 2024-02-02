import pandas as pd
from datetime import datetime
from tkinter import filedialog, Tk

def generate_dummy_data(row):
    if pd.isna(row.get('FirstName', None)):
        row['FirstName'] = 'N/A'
    if pd.isna(row.get('LastName', None)):
        row['LastName'] = 'N/A'
    if pd.isna(row.get('Cellphone', None)):
        row['Cellphone'] = '0000000000'
    if pd.isna(row.get('CreatedOnDateTime', None)):
        row['CreatedOnDateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if pd.isna(row.get('DateOfBirth', None)):
        row['DateOfBirth'] = '1901-01-01 00:00:00'
    if pd.isna(row.get('GendersId', None)):
        row['GendersId'] = 1
    if pd.isna(row.get('StatusId', None)):
        row['StatusId'] = 1
    if pd.isna(row.get('TitlesId', None)):
        row['TitlesId'] = 1
    return row

def process_csv():
    root = Tk()
    root.withdraw()  # Hide the main window

    # Ask the user to select the input CSV file
    input_csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    # Check if the user selected a file
    if not input_csv_path:
        print("No input file selected. Exiting.")
        return

    # Ask the user to select the output CSV file
    output_csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    # Check if the user selected a file
    if not output_csv_path:
        print("No output file selected. Exiting.")
        return

    # Read the CSV file with potential leading/trailing whitespaces in column names
    df = pd.read_csv(input_csv_path, skipinitialspace=True)

    # Generate dummy data for empty fields
    df = df.apply(generate_dummy_data, axis=1)

    # Save the result as a new CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Processing complete. Result saved to {output_csv_path}")

if __name__ == "__main__":
    process_csv()

