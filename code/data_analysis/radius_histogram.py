import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

def process_csv_file(csv_path, output_folder, summary_data):
    """
    Process a single CSV file: calculate deviations from the prominent peak,
    save processed data, generate a histogram plot, and update summary data.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Load data and check for 'Radius(mm)' column
    df = pd.read_csv(csv_path)
    if 'Radius(mm)' not in df.columns:
        raise KeyError(f"'Radius(mm)' column not found in {csv_path}. Available columns: {df.columns}")
    
    # Extract radius data
    data = df['Radius(mm)'].to_numpy()
    
    # Compute statistical metrics
    mean_radius = np.mean(data)
    
    # Compute histogram
    hist_counts, hist_bins = np.histogram(data, bins=100)
    bin_centers = (hist_bins[:-1] + hist_bins[1:]) / 2
    
    # Apply Gaussian smoothing to histogram counts
    smoothed_hist = gaussian_filter1d(hist_counts, sigma=2)
    
    # Detect peaks using scipy.signal.find_peaks
    peaks, _ = find_peaks(smoothed_hist, height=np.mean(smoothed_hist))
    
    # Find prominent peak (highest peak in smoothed histogram)
    if len(peaks) > 0:
        prominent_peak_index = peaks[np.argmax(smoothed_hist[peaks])]
        prominent_peak = bin_centers[prominent_peak_index]
        detected_peaks = bin_centers[peaks]
    else:
        prominent_peak = np.nan  # If no peaks are detected, set prominent peak to NaN
        detected_peaks = []
    
    # Calculate deviation from the prominent peak
    df['Deviation_from_Peak'] = df['Radius(mm)'] - prominent_peak
    
    # Calculate mean deviation from the prominent peak
    mean_deviation_from_peak = np.mean(np.abs(df['Deviation_from_Peak']))
    
    # Save processed data to CSV
    processed_filename = os.path.splitext(os.path.basename(csv_path))[0] + '_processed.csv'
    processed_path = os.path.join(output_folder, processed_filename)
    df.to_csv(processed_path, index=False)
    
    # Update summary data with detected peaks and deviations
    summary_data.append({
        'File': csv_path,
        'Mean Radius': mean_radius,
        'Prominent Peak': prominent_peak,
        'Mean Deviation from Peak': mean_deviation_from_peak,
        'Detected Peaks': detected_peaks.tolist()  # Convert NumPy array to list for saving
    })
    
    # Plot histogram and detected peaks
    plt.figure(figsize=(12, 6))
    plt.bar(bin_centers, hist_counts, width=(hist_bins[1] - hist_bins[0]), alpha=0.4)
    plt.plot(bin_centers, smoothed_hist, label="Smoothed Histogram", color='red', linewidth=2)
    
    # if len(peaks) > 0:
        # plt.scatter(bin_centers[peaks], smoothed_hist[peaks], color='blue', s=100, label="Detected Peaks")
        # plt.axvline(prominent_peak, color='cyan', linestyle='--', linewidth=2,
                    # label=f'Prominent Peak: {prominent_peak:.4f} mm')
    
    plt.xlabel("Radius (mm)")
    plt.xlim(0.8,2.4)
    plt.ylabel("Frequency")
    plt.title(f"Histogram for {os.path.basename(csv_path)}")
    plt.legend()
    
    # Save plot to file
    plot_filename = os.path.splitext(os.path.basename(csv_path))[0] + '_histogram.png'
    plot_path = os.path.join(output_folder, plot_filename)
    plt.savefig(plot_path)
    plt.close()

def process_nested_folders(input_folder, output_base_folder):
    """
    Process all CSV files in nested folders and generate a summary file.
    """
    summary_data = []  # List to store summary information for all files
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):  # Process only CSV files
                csv_path = os.path.join(root, file)
                
                # Create corresponding output subfolder
                relative_path = os.path.relpath(root, input_folder)
                output_folder = os.path.join(output_base_folder, relative_path)
                
                try:
                    # Process the CSV file and update summary data
                    process_csv_file(csv_path, output_folder, summary_data)
                except KeyError as e:
                    print(f"Skipping {csv_path}: {e}")
    
    # Save summary data to a single CSV file in the output base folder
    summary_df = pd.DataFrame(summary_data)
    summary_file_path = os.path.join(output_base_folder, 'summary.csv')
    summary_df.to_csv(summary_file_path, index=False)

# Set input and output folders
input_folder = r'Input folder path'  # Replace with your input folder path containing CSVs
output_folder = r'Output folder path'  # Replace with your desired output folder path

# Process all CSV files in nested folders
process_nested_folders(input_folder, output_folder)

print("Processing complete!")