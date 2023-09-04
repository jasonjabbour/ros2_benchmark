import gspread
import os
from wasabi import color


# For context about how to get the authentication json.
MAINTAINER_NAME = 'Jason Jabbour'
MAINTAINER_EMAIL = 'jasonjabbour@g.harvard.edu'

class DataUploader():
    def __init__(self, json_file_path) -> None:
        self.client = self._authenticate(json_file_path)

        self.valid_method_types = ['grey', 'black']

    def _authenticate(self, json_file_path):

        # Check if the JSON file exists
        if not os.path.exists(json_file_path):
            print(color(os.getcwd(), fg="red"))
            print(color(f"The specified Google Authentication JSON file: {json_file_path} does not exist.", fg="red"))
            print(color(f"Please contact {MAINTAINER_NAME} <{MAINTAINER_EMAIL}> to receive the Google Authentication JSON File.", fg="red"))
            return None

        try:
            # Authenticate using the service account file
            client = gspread.service_account(filename=json_file_path)
            
            # Try fetching a list of spreadsheets to check if the client is valid.
            client.list_spreadsheet_files()

        except Exception as e:
            print(color(f"Failed to authenticate or interact with the Google Sheets API: {e}", fg="red"))
            return None
        
        return client

    def upload_data_helper(self, sheet, base_column_name, data):
        # Get the existing column headers from the first row
        existing_headers = sheet.row_values(1)
        counter = 1  # Initialize counter for numbering columns with similar names
        column_name = f"{base_column_name}:Sample_{counter}"

        # Check for duplicate column names and increment counter if found
        while column_name in existing_headers:
            counter += 1
            column_name = f"{base_column_name}:Sample_{counter}"

        # Calculate the last column index based on the existing headers
        last_col = len(existing_headers) + 1

        # Check if the sheet needs additional columns, if so, add them
        sheet_cols = sheet.col_count
        if last_col > sheet_cols:
            sheet.add_cols(last_col - sheet_cols)

        # Update the header cell for the new column
        sheet.update_cell(1, last_col, column_name)

        # Create the range for the new column's data
        col_letter = gspread.utils.rowcol_to_a1(1, last_col).rstrip("1")
        cell_range = f"{col_letter}2:{col_letter}{len(data) + 1}"

        # Populate the new column with data
        sheet.update(cell_range, [[value] for value in data])


    def upload_latency_data(self, sheet, benchmark_name, method_type, hardware, fps, rosbag_name, latency_data):
        base_column_name = f'{benchmark_name}:{method_type}:{hardware}:{fps}:{rosbag_name}:latency'
        self.upload_data_helper(sheet, base_column_name, latency_data)
        print(color(f"Latency Data uploaded to Google Sheet!", fg="green"))


    def upload_cpu_usage_data(self, sheet, benchmark_name, method_type, hardware, fps, rosbag_name, cpu_usage_data):
        # Flatten the cpu_usage_data list of lists into a single list
        flattened_cpu_data = [data for core_data in cpu_usage_data for data in core_data]
        total_cores = len(cpu_usage_data)
        base_column_name = f'{benchmark_name}:{method_type}:{hardware}:{fps}:{rosbag_name}:CPU_Cores_{total_cores}'
        self.upload_data_helper(sheet, base_column_name, flattened_cpu_data)
        print(color(f"CPU Usage Data Uploaded to Google Sheet!", fg="green"))


    def upload_power_data(self, sheet, benchmark_name, method_type, hardware, fps, rosbag_name, power_data):
        # TODO: Make sure power_data is a 1D list of values
        base_column_name = f'{benchmark_name}:{method_type}:{hardware}:{fps}:{rosbag_name}:power'
        self.upload_data_helper(sheet, base_column_name, power_data)
        print(color(f"Power Data Uploaded to Google Sheet!", fg="green"))


    def upload_data(self, 
                    google_sheet_url,
                    benchmark_name,
                    method_type, 
                    hardware, 
                    fps, 
                    rosbag_path,
                    latency_data=None,
                    cpu_usage_data=None,
                    power_data=None):

        if self.client is None:
            print(color("No Data Uploaded. Google SpreadSheet Client Unavailable.", fg="red"))
            return
        
        if method_type.lower() not in self.valid_method_types:
            method_type = 'No Method'
            print(color(f"Invalid method type: {method_type}. Must be: {self.valid_method_types}. Using '{method_type}' in column header.", fg="red"))
        
        # Get rosbag name
        rosbag_name = os.path.basename(rosbag_path)

        # Open the Google Sheet using its URL
        sheet = self.client.open_by_url(google_sheet_url).sheet1

        if latency_data is not None:
            # Upload latency data to the sheet
            self.upload_latency_data(sheet, benchmark_name, method_type, hardware, fps, rosbag_name, latency_data)
        if cpu_usage_data is not None:
            # Upload CPU usage data to the sheet
            self.upload_cpu_usage_data(sheet, benchmark_name, method_type, hardware, fps, rosbag_name, cpu_usage_data)
        if power_data is not None:
            # Upload Power Data
            # TODO: check the TODO inside the upload_power_data() function 
            self.upload_power_data(sheet, benchmark_name, method_type, hardware, fps, rosbag_name, power_data)



