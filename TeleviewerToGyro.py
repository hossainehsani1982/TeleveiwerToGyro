import csv
import numpy as np
import os
from datetime import datetime


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
############################################################################################################

def main():
    global declination, sample_intervals, casing_height, tool_name, hole_id

    print("Welcome to CSV Converter!")
    input_file = input("Please enter the input file path: ").strip()

    while True:
        declination_input = input("Please enter the declination value (default is 19.1): ").strip()
        if not declination_input:
            break
        try:
            declination = float(declination_input)
            break
        except ValueError:
            print("Please enter a valid declination value.")

    while True:
        sample_intervals_input = input("Please enter desired intervals (enter '0' to get all data): ").strip()
        if not sample_intervals_input:
            break
        try:
            sample_intervals = int(sample_intervals_input)
            break
        except ValueError:
            print("Please enter a valid sample interval value.")

    while True:
        casing_height_input = input("Please enter casing height (default is 15): ").strip()
        if not casing_height_input:
            break
        try:
            casing_height = float(casing_height_input)
            break
        except ValueError:
            print("Please enter a valid casing height value.")

    while True:
        tool_name = input("Please enter the tool name (default is 'gyro'): ").strip().upper()
        if tool_name:
            break
        else:
            print("Tool name cannot be empty. Please enter a valid tool name.")

    while True:
        hole_id = input("Please enter the hole ID (default is 'hole'): ").strip()
        if hole_id:
            break
        else:
            print("Hole ID cannot be empty. Please enter a valid hole ID.")

    ask_project_code()

    output = create_output_file(input_file)

    print(f"Conversion complete. Output saved to: {output}")

############################################################################################################
def ask_project_code():
    global project_code
    ask = input("Do you want to enter a project code? (y/n): ").strip()
    if ask.lower() == 'y':
        project_code = input("Please enter the project code: ").strip().upper()
    else:
        project_code = None

############################################################################################################

def create_output_file(input_file):
    global hole_id, tool_name, project_code
    file_counter = 1

    input_file_directory = os.path.dirname(input_file)

    if project_code:
        output_file = os.path.join(input_file_directory, f"{project_code}_{hole_id}_Gy_{tool_name}_{file_counter}_{get_date()}.csv")
    else:
        output_file = os.path.join(input_file_directory, f"{hole_id}_Gy_{tool_name}_{file_counter}_{get_date()}.csv")

    read_text_file(input_file, check_output_file(output_file, file_counter))

############################################################################################################
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

############################################################################################################

def read_text_file(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    create_data(lines, output_file)

############################################################################################################

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

############################################################################################################

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

############################################################################################################

def azimuth_correction(azimuth):
    return float(azimuth) - 360 if float(azimuth) > 360 else float(azimuth)

############################################################################################################

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

############################################################################################################

def create_csv_file(gyros, headers, output_file):
    global hole_id, tool_name, project_code
    with open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["",headers.depth, headers.tilt, headers.azimuth])
        for gyro in gyros:
            if project_code is not None:
                csv_writer.writerow([f"{project_code}_{hole_id}", gyro.depth, gyro.tilt, gyro.azimuth, tool_name])
            else:
                csv_writer.writerow([hole_id, gyro.depth, gyro.tilt, gyro.azimuth, tool_name])


if __name__ == "__main__":
    main()
