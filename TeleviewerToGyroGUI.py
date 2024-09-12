import csv
import numpy as np
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

sample_intervals = None
casing_height = None
declination = None
tool_name = None
hole_id = None
project_code = None


class Gyro:
    def __init__(self, depth, tilt, azimuth):
        self.depth = depth
        self.tilt = tilt
        self.azimuth = azimuth

    def print_gyro(self):
        print(f"Depth: {self.depth}, Tilt: {self.tilt}, Azimuth: {self.azimuth}")


class DrillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gyro_Converter")

        # Make the grid resizable
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(7, weight=1)

        # Input File
        tk.Label(root, text="Select Input File:").grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.input_file_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.input_file_button.grid(row=0, column=1, sticky="ew")

        # Declination
        tk.Label(root, text="Enter Declination Value (default is 19.1):").grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.declination_input = tk.Entry(root)
        self.declination_input.grid(row=1, column=1, sticky="ew")

        # Sample Intervals
        tk.Label(root, text="Enter Sample Intervals (enter '0' to get all data):").grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.sample_intervals_input = tk.Entry(root)
        self.sample_intervals_input.grid(row=2, column=1, sticky="ew")

        # Casing Height
        tk.Label(root, text="Enter Casing Height (default is 15):").grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.casing_height_input = tk.Entry(root)
        self.casing_height_input.grid(row=3, column=1, sticky="ew")

        # Tool Name
        tk.Label(root, text="Enter Tool Name (default is 'gyro'):").grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.tool_name_input = tk.Entry(root)
        self.tool_name_input.grid(row=4, column=1, sticky="ew")

        # Hole ID
        tk.Label(root, text="Enter Hole ID (default is 'hole'):").grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        self.hole_id_input = tk.Entry(root)
        self.hole_id_input.grid(row=5, column=1, sticky="ew")

        # Project Code
        tk.Label(root, text="Enter Project Code (optional):").grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        self.project_code_input = tk.Entry(root)
        self.project_code_input.grid(row=6, column=1, sticky="ew")

        # Submit button
        tk.Button(root, text="Submit", command=self.submit).grid(row=7, column=0, columnspan=2, pady=20, sticky="ew")

    def browse_file(self):
        self.input_file_path = askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not self.input_file_path:
            messagebox.showerror("Input Error", "No file selected. Please select a valid input file.")
        else:
            self.input_file_button.config(text=os.path.basename(self.input_file_path))

    def submit(self):
        global declination, sample_intervals, casing_height, tool_name, hole_id, project_code

        # Get and validate declination
        declination_input = self.declination_input.get().strip() or '19.1'
        try:
            declination = float(declination_input)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid declination value.")
            return

        # Get and validate sample intervals
        sample_intervals_input = self.sample_intervals_input.get().strip() or '5'
        try:
            sample_intervals = int(sample_intervals_input)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid sample interval value.")
            return

        # Get and validate casing height
        casing_height_input = self.casing_height_input.get().strip() or '15'
        try:
            casing_height = float(casing_height_input)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid casing height value.")
            return

        # Get tool name
        tool_name = self.tool_name_input.get().strip().upper() or 'GYRO'
        if not tool_name:
            messagebox.showerror("Input Error", "Tool name cannot be empty.")
            return

        # Get hole ID
        hole_id = self.hole_id_input.get().strip() or 'hole'
        if not hole_id:
            messagebox.showerror("Input Error", "Hole ID cannot be empty.")
            return

        # Get project code (optional)
        project_code = self.project_code_input.get().strip().upper() or None

        # Confirm and start the file processing
        if self.input_file_path:
            create_output_file(self.input_file_path)
            messagebox.showinfo("Success", "Conversion complete.")
        else:
            messagebox.showerror("Input Error", "Please select a valid input file.")


def create_output_file(input_file):
    global hole_id, tool_name, project_code
    file_counter = 1

    input_file_directory = os.path.dirname(input_file)

    if project_code:
        output_file = os.path.join(input_file_directory, f"{project_code}_{hole_id}_Gy_{tool_name}_{file_counter}_{get_date()}.csv")
    else:
        output_file = os.path.join(input_file_directory, f"{hole_id}_Gy_{tool_name}_{file_counter}_{get_date()}.csv")

    read_text_file(input_file, check_output_file(output_file, file_counter))


def check_output_file(output_file, file_counter):
    if os.path.exists(output_file):
        while True:
            file_counter += 1
            output_file = output_file.replace(f"_{file_counter-1}_", f"_{file_counter}_")
            if not os.path.exists(output_file):
                return output_file
    else:
        return output_file


def get_date():
    return datetime.now().strftime("%m%d%Y")


def read_text_file(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    create_data(lines, output_file)


def create_data(lines, output_file):
    global sample_intervals, casing_height
    gyros = []
    for line in lines:
        cleaned_line = ' '.join(line.split())
        if cleaned_line:
            columns = cleaned_line.split()
            gyro = create_obj(columns)
            gyros.append(gyro)

    final_gyros = calculate_interval(gyros, sample_intervals, casing_height)

    create_csv_file(final_gyros, gyros[0], output_file)


depth_index = None
tilt_index = None
azimuth_index = None


def create_obj(columns):
    global declination, depth_index, tilt_index, azimuth_index

    if depth_index and tilt_index and azimuth_index is None:
        return Gyro(depth=columns[depth_index], tilt=columns[tilt_index], azimuth=columns[azimuth_index])
    for i, col in enumerate(columns):
        if "DEPT" in col.upper():
            depth_index = i
        elif "TILT" in col.upper():
            tilt_index = i
        elif "AZIMUTH" in col.upper():
            azimuth_index = i
    try:
        columns[azimuth_index] = str(float(columns[azimuth_index]) + declination)
        if float(columns[azimuth_index]) > 360:
            columns[azimuth_index] = azimuth_correction(columns[azimuth_index])
        return Gyro(depth=columns[depth_index], tilt=columns[tilt_index], azimuth=columns[azimuth_index])
    except (ValueError, IndexError):
        return Gyro(depth=columns[depth_index], tilt=columns[tilt_index], azimuth=columns[azimuth_index])


def azimuth_correction(azimuth):
    return float(azimuth) - 360 if float(azimuth) > 360 else float(azimuth)


def calculate_interval(gyros, sample_intervals, casing_height):
    d_gyros = []
    added_depth = []
    final_gyros = []

    for gyro in gyros[1:]:
        if int(float(gyro.depth)) >= casing_height:
            d_gyros.append(gyro)

    for gyro in d_gyros:
        if gyro.depth not in added_depth:
            added_depth.append(gyro.depth)
            final_gyros.append(gyro)

    valid_gyros = []
    for g in d_gyros:
        if not (-1000 <= float(g.tilt) <= 1000 and -1000 <= float(g.azimuth) <= 1000):
            continue  
        valid_gyros.append(g)

    final_gyros = valid_gyros

    interpolated_gyros = []
    start_depth = int(float(final_gyros[0].depth))
    end_depth = int(float(final_gyros[-1].depth))

    for depth in np.arange(start_depth, end_depth, sample_intervals):
        closest_gyro = min(final_gyros, key=lambda g: abs(int(float(g.depth)) - depth))

        interpolated_gyros.append(Gyro(depth=depth, tilt=closest_gyro.tilt, azimuth=closest_gyro.azimuth))

        interpolated_gyros[-1].print_gyro()

    print(f"Total interpolated gyros: {len(interpolated_gyros)}")

    return interpolated_gyros


def create_csv_file(gyros, headers, output_file):
    global hole_id, tool_name, project_code
    with open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["", headers.depth, headers.tilt, headers.azimuth])
        for gyro in gyros:
            if project_code is not None:
                csv_writer.writerow([f"{project_code}_{hole_id}", gyro.depth, gyro.tilt, gyro.azimuth, tool_name])
            else:
                csv_writer.writerow([hole_id, gyro.depth, gyro.tilt, gyro.azimuth, tool_name])


if __name__ == "__main__":
    root = tk.Tk()
    app = DrillingApp(root)
    root.mainloop()
