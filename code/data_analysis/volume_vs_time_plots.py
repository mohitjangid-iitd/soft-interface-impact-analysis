import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate volume from radius
def calculate_volume(radius):
    return (4/3) * np.pi * (radius ** 3)

# Function to process CSV files while keeping the folder structure
def process_csv_files(root_folder, output_folder):
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.csv'):
                file_path = os.path.join(foldername, filename)

                try:
                    df = pd.read_csv(file_path)

                    # MODIFY COLUMN NAMES HERE IF NEEDED
                    if 'Time(Sec)' in df.columns and 'Radius(mm)' in df.columns:
                        df.rename(columns={'Time(Sec)': 'time', 'Radius(mm)': 'radius'}, inplace=True)
                    else:
                        print(f"Skipping {filename}: Required columns missing")
                        continue

                    # Calculate volume
                    df['volume'] = calculate_volume(df['radius'])

                    # Preserve folder structure in output directory
                    relative_path = os.path.relpath(foldername, root_folder)
                    output_subfolder = os.path.join(output_folder, relative_path)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)  # Create subfolders

                    # Plot and save graph
                    plot_and_save(df, filename, output_subfolder)

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

# Function to plot and save images in corresponding nested folders
def plot_and_save(df, filename, output_folder):
    plt.figure(figsize=(10, 6))
    plt.scatter(df['time'], df['volume'], marker='o')
    
    plt.xlabel("Time (Sec)")
    plt.ylabel(r"Volume $(mm^3)$")  # Proper LaTeX for mm³
    plt.title(f"Time vs Volume - {filename}")
    plt.ylim(0,40)
    # plt.legend()
    plt.grid(True)

    # Save plot in the corresponding nested folder
    image_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.png")
    plt.savefig(image_path, dpi=300)
    plt.close()  # Close plot to avoid memory issues

    print(f"Saved plot: {image_path}")

# Set your root directory containing CSV files
root_directory = "C:/Users/Admin/Desktop/New 2/water/500fps_results/20250113/0.8mm_results"
output_directory = "C:/Users/Admin/Desktop/New 2/water/Vol vs time scale/20250113/0.8mm_results"  # Folder to save plots

# Process and plot
process_csv_files(root_directory, output_directory)