import csv
import numpy as np
import matplotlib.pyplot as plt

def plot_from_two_csvs(csv_file_path_1, csv_file_path_2):
    depths_1 = []
    azimuths_1 = []
    
    depths_2 = []
    azimuths_2 = []

    # Read the first CSV file
    with open(csv_file_path_1, 'r') as file1:
        reader = csv.DictReader(file1)
        for row in reader:
            try:
                depth = round(float(row['DEPT[M]']), 2)
                azimuth = round(float(row['AZIMUTH_(A']), 2)
                
                depths_1.append(depth)
                azimuths_1.append(azimuth)  
            except ValueError:
                print(f"Skipping invalid row in file 1: {row}")

    # Read the second CSV file
    with open(csv_file_path_2, 'r') as file2:
        reader = csv.DictReader(file2)
        for row in reader:
            try:
                dist = round(float(row['Dist']), 2) 
                azimuth = round(float(row['Azim']), 2)
                
                depths_2.append(dist)
                azimuths_2.append(azimuth) 
            except ValueError:
                print(f"Skipping invalid row in file 2: {row}")

    # Generate polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # Convert azimuths from degrees to radians for polar plot (still required for plotting)
    azimuths_1_radians = np.radians(azimuths_1)
    azimuths_2_radians = np.radians(azimuths_2)
    
    # Plot the first dataset (file 1)
    ax.plot(azimuths_1_radians, depths_1, 'o', color='purple', label="File 1: Depth vs Azimuth")
    
    # Plot the second dataset (file 2)
    ax.plot(azimuths_2_radians, depths_2, 'o', color='green', label="File 2: Dist vs Azim")

    # Customize plot
    ax.set_theta_direction(-1)  # Reverse the direction of angles (clockwise)
    ax.set_theta_offset(np.pi / 2.0)  # Set 0° at the top (north)
    ax.set_rlabel_position(0)  # Set radial label position away from the ticks

    # Set azimuth ticks (in degrees) at 10° increments
    ax.set_xticks(np.radians(np.arange(0, 360, 10)))  # Use np.arange to set ticks at every 10°

    # Move the legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1.1, 1.05))

    plt.title("Polar Plot: Comparison of Two Datasets")
    plt.tight_layout()
    plt.show()


# Test the function with your two CSV file paths
csv_file_path_1 = r'H:\DGI\desktop\Projects\L-891_SeaBridge\3A24-406\L-891_3a24-406_Gy_OTV_1_09052024.csv' 
csv_file_path_2 = r'H:\DGI\desktop\Projects\L-891_SeaBridge\3A24-406\survey_3Aces_Master.csv'
plot_from_two_csvs(csv_file_path_1, csv_file_path_2)


