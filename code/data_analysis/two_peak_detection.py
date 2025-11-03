import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

# Load the CSV file
file_name = 'CSV file path'
data = pd.read_csv(file_name)

# Extract the 'Radius(mm)' column and drop NaN values
radius_data = data['Radius(mm)'].dropna().values

# Generate a histogram and smooth it using KDE (Kernel Density Estimation)
kde = gaussian_kde(radius_data)
x_values = np.linspace(min(radius_data), max(radius_data), 1000)
smoothed_histogram = kde(x_values)

# Find peaks in the smoothed histogram and their properties (e.g., height)
peaks, properties = find_peaks(smoothed_histogram, height=0)  # 'height' gives prominence values

# Ensure there are at least two peaks detected
if len(peaks) < 2:
    raise ValueError("Less than two peaks detected in the data. Adjust peak detection parameters.")

# Sort peaks by their prominence (height) in descending order and select the two most prominent ones
sorted_indices = np.argsort(properties['peak_heights'])[::-1]  # Sort by height descending
top_two_peaks = sorted_indices[:2]  # Indices of the two most prominent peaks

# Get the x-values of the two most prominent peaks
prominent_peak_positions = x_values[peaks[top_two_peaks]]
sorted_peaks = np.sort(prominent_peak_positions)  # Sort these two peaks by position for logical splitting

# Determine the cutting point (midpoint between the two most prominent peaks)
cutting_point = np.mean(sorted_peaks)

# Split data into two subsets based on the cutting point
subset1 = radius_data[radius_data <= cutting_point]
subset2 = radius_data[radius_data > cutting_point]

# Calculate standard deviations for each subset
std_dev1 = np.std(subset1)
std_dev2 = np.std(subset2)

# Plot histogram, KDE, and detected peaks for visualization
plt.figure(figsize=(10, 6))
plt.hist(radius_data, bins=50, density=True, alpha=0.5, label='Raw Histogram')
plt.plot(x_values, smoothed_histogram, color='red', label='Smoothed Histogram')
plt.scatter(x_values[peaks], smoothed_histogram[peaks], color='blue', label='Detected Peaks')
plt.axvline(cutting_point, color='cyan', linestyle='--', label=f'Cutting Point: {cutting_point:.4f} mm')
for i, peak in enumerate(sorted_peaks):
    plt.annotate(f'Peak {i + 1}: {peak:.4f} mm', (peak, kde(peak)[0]), textcoords="offset points", xytext=(-20,10), ha='center')

plt.title(f"Histogram for {file_name.split('/')[-1]}")
plt.xlabel("Radius (mm)")
plt.ylabel("Frequency")
plt.legend()
plt.show()

# Output results
print(f"First Peak: {sorted_peaks[0]:.4f} mm, Standard Deviation: {std_dev1:.4f}")
print(f"Second Peak: {sorted_peaks[1]:.4f} mm, Standard Deviation: {std_dev2:.4f}")