import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

def find_global_min_max(input_folder):
    """
    Scan all CSV files and find the global minimum and maximum of the transformed area data.
    """
    min_val, max_val = np.inf, -np.inf
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):
                csv_path = os.path.join(root, file)
                df = pd.read_csv(csv_path)
                if 'Radius(mm)' in df.columns:
                    data = df['Radius(mm)'].to_numpy()
                    data = data**2 * np.pi  # Convert radius to area
                    min_val = min(min_val, np.min(data))
                    max_val = max(max_val, np.max(data))
                    
    return min_val, max_val

def process_csv_file(csv_path, output_folder, summary_data, bin_edges):
    """
    Process a single CSV file with fixed binning.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    if 'Radius(mm)' not in df.columns:
        raise KeyError(f"'Radius(mm)' column not found in {csv_path}. Available columns: {df.columns}")
    
    data = df['Radius(mm)'].to_numpy()
    data = data**2 * np.pi  # Convert radius to area
    
    mean_radius = np.mean(data)
    
    # Fixed binning
    hist_counts, _ = np.histogram(data, bins=bin_edges)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Normalize to probability density
    density_counts = hist_counts / (np.sum(hist_counts) * bin_width)
    
    # Smooth
    smoothed_hist = gaussian_filter1d(density_counts, sigma=2)
    
    # Find peaks
    peaks, _ = find_peaks(smoothed_hist, height=np.mean(smoothed_hist))
    
    if len(peaks) > 0:
        prominent_peak_index = peaks[np.argmax(smoothed_hist[peaks])]
        prominent_peak = bin_centers[prominent_peak_index]
        detected_peaks = bin_centers[peaks]
    else:
        prominent_peak = np.nan
        detected_peaks = []
    
    deviation_from_peak = data - prominent_peak
    mean_deviation_from_peak = np.mean(np.abs(deviation_from_peak))
    
    summary_data.append({
        'File': csv_path,
        'Mean Radius': mean_radius,
        'Prominent Peak': prominent_peak,
        'Mean Deviation from Peak': mean_deviation_from_peak,
        'Detected Peaks': detected_peaks.tolist()
    })
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.bar(bin_centers, density_counts, width=bin_width, alpha=0.4)
    plt.plot(bin_centers, smoothed_hist, label="Smoothed Histogram", color='red', linewidth=2)
    plt.xlabel(r"Area of Drop($mm^2$)", fontsize=22)
    plt.xlim(bin_edges[0], bin_edges[-1])
    plt.ylabel("Probability Density", fontsize=22)
    plt.title(f"Histogram for {os.path.basename(csv_path)}", fontsize=28)
    plt.legend()
    plt.tick_params(axis='both', labelsize=18)  # Added to adjust tick label size
    
    plot_filename = os.path.splitext(os.path.basename(csv_path))[0] + '_histogram.png'
    plot_path = os.path.join(output_folder, plot_filename)
    plt.savefig(plot_path)
    # plt.show()
    plt.close()

def process_nested_folders(input_folder, output_base_folder):
    """
    Process all CSV files with fixed binning and generate summary.
    """
    summary_data = []
    
    # Step 1: Find global min and max
    global_min, global_max = find_global_min_max(input_folder)
    print(f"Global data range: {global_min:.4f} to {global_max:.4f}")
    
    # Define fixed bins
    bin_edges = np.linspace(global_min, global_max, 150)  # 100 bins between min and max
    
    # Step 2: Process each file
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):
                csv_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_folder)
                output_folder = os.path.join(output_base_folder, relative_path)
                
                try:
                    process_csv_file(csv_path, output_folder, summary_data, bin_edges)
                except KeyError as e:
                    print(f"Skipping {csv_path}: {e}")
    
    # Save summary
    summary_df = pd.DataFrame(summary_data)
    summary_file_path = os.path.join(output_base_folder, 'summary.csv')
    summary_df.to_csv(summary_file_path, index=False)

# Set input and output folders
input_folder = r'Input folder'
output_folder = r'Output folder'

process_nested_folders(input_folder, output_folder)

print("Processing complete!")