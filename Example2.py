import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from io import StringIO


class CSVEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Editor")

        # File selection button
        self.select_button = tk.Button(root, text="Select CSV File", command=self.select_file)
        self.select_button.pack(pady=10)

        # Columns listbox
        self.columns_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
        self.columns_listbox.pack(pady=10)

        # Remove columns button
        self.remove_button = tk.Button(root, text="Remove Selected Columns", command=self.remove_columns)
        self.remove_button.pack(pady=10)

        # Save button
        self.save_button = tk.Button(root, text="Save as CSV", command=self.save_csv)
        self.save_button.pack(pady=10)

        # Get Error Report button
        self.error_report_button = tk.Button(root, text="Get Error Report", command=self.get_error_report)
        self.error_report_button.pack(pady=10)

        # Selected file path and loaded DataFrame
        self.file_path = None
        self.df = None

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.load_csv()

    def load_csv(self):
        try:
            # Use the modified function for CSV parsing with error handling
            self.df = self.parse_csv_with_errors(self.file_path)
            self.update_columns_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing CSV file: {e}")

    def parse_csv_with_errors(self, csv_path):
        try:
            # Read CSV with on_bad_lines='skip'
            self.df = pd.read_csv(csv_path, encoding='ISO-8859-1', on_bad_lines='skip', dtype=str, low_memory=False)
        except pd.errors.ParserError as e:
            print(f"Error during CSV parsing: {e}")
            return None

        return self.df

    def update_columns_listbox(self):
        self.columns_listbox.delete(0, tk.END)
        if self.df is not None:
            for col in self.df.columns:
                self.columns_listbox.insert(tk.END, col)

    def remove_columns(self):
        selected_indices = self.columns_listbox.curselection()
        selected_columns = [self.columns_listbox.get(idx) for idx in selected_indices]
        if self.df is not None:
            self.df = self.df.drop(columns=selected_columns)
            self.update_columns_listbox()

    def save_csv(self):
        if self.df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                self.df.to_csv(save_path, index=False)
                messagebox.showinfo("Save Successful", "CSV file saved successfully.")

    def get_error_report(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path = file_path
            error_lines = self.detect_error_lines()
            if error_lines:
                self.save_error_report(error_lines)
            else:
                messagebox.showinfo("No Errors", "No errors found in the CSV file.")

    def detect_error_lines(self):
        error_lines = []

        # Read the CSV file and store columns causing errors
        try:
            pd.read_csv(self.file_path, encoding='ISO-8859-1', dtype=str, low_memory=False)
        except pd.errors.ParserError:
            with open(self.file_path, 'r', encoding='ISO-8859-1') as file:
                for line_number, line in enumerate(file, start=1):
                    # Skip empty lines
                    if not line.strip():
                        continue

                    try:
                        # Attempt to parse the line using StringIO
                        pd.read_csv(StringIO(line), encoding='ISO-8859-1', dtype=str, low_memory=False)
                    except pd.errors.ParserError:
                        # Capture the line causing the error
                        error_lines.append((line_number, line))
                        print(f"Error in line {line_number}: {line}")

            # Display alert with the count of total columns
            tk.messagebox.showinfo("Total Columns Count", f"Total number of columns: {len(self.df.columns)}")

        return error_lines

    def save_error_report(self, error_lines):
        if error_lines:
            error_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

            # Save error lines to the specified text file
            with open(error_file_path, 'w') as error_file:
                for line_number, line in error_lines:
                    error_file.write(f"Error in line {line_number}: {line}\n")

            messagebox.showinfo("Error Report Saved", "Error report saved successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVEditorApp(root)
    root.mainloop()
