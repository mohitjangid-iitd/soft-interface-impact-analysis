import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from Functions import crop

# Set base input and output folders
input_base = r'Input folder path'
output_base = r'output folder path'

# Define fixed subfolders
csv_folder = os.path.join(output_base, 'csv')
line_plot_folder = os.path.join(output_base, 'plots', 'line')
histogram_folder = os.path.join(output_base, 'plots', 'hist')

# Create those folders if they don’t exist
os.makedirs(csv_folder, exist_ok=True)
os.makedirs(line_plot_folder, exist_ok=True)
os.makedirs(histogram_folder, exist_ok=True)

# Threshold and morphology settings
threshold_value = 150  
kernel = np.ones((5, 5), np.uint8)

# Functions
def get_row_intensity(binary_roi):
    return np.mean(binary_roi, axis=1)

def find_first_zero_row(row_intensities):
    zero_rows = np.where(row_intensities == 0)[0]
    return zero_rows[0] if zero_rows.size > 0 else -1

def process_video(video_path, video_name_wo_ext):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    zero_rows_per_frame = []
    frame_numbers = []
    frame_no = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

        roi = crop(binary, 0.47, 0, 0.1, 1)  # Adjust if needed
        roi_filled = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, kernel, iterations=2)

        row_intensities = get_row_intensity(roi_filled)
        first_zero_row = find_first_zero_row(row_intensities)

        zero_rows_per_frame.append(first_zero_row)
        frame_numbers.append(frame_no)

        frame_no += 1

    cap.release()

    # Save CSV
    df = pd.DataFrame({'Frame': frame_numbers, 'Jet Length (pixels)': zero_rows_per_frame})
    csv_path = os.path.join(csv_folder, f'{video_name_wo_ext}_jet_length_data.csv')
    df.to_csv(csv_path, index=False)
    Frame_no=np.array(frame_numbers)/500
    Jet_l=np.array(zero_rows_per_frame)*96/1280
    # Plot line graph
    plt.figure(figsize=(10, 5))
    plt.plot(Frame_no, Jet_l, marker='o', linestyle='-', color='b', markersize=3)
    plt.xlabel("Time (Sec)")
    plt.ylabel("Jet Length (mm)")
    # plt.title(f"Jet Length vs Frame Number\n({video_name_wo_ext})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(line_plot_folder, f'{video_name_wo_ext}_jet_length_plot.png'))
    plt.close()

    # Plot histogram
    plt.figure(figsize=(8, 4))
    plt.hist([val for val in Jet_l if val != -1], bins=30, color='green', edgecolor='black',density=True)
    plt.xlabel("Jet Length (mm)")
    plt.ylabel("Prob. Density")
    # plt.title(f"Histogram of Jet Length\n({video_name_wo_ext})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(histogram_folder, f'{video_name_wo_ext}_jet_length_histogram.png'))
    plt.close()

# Walk through folders
for root, dirs, files in os.walk(input_base):
    for file in files:
        if file.lower().endswith('.avi'):
            input_path = os.path.join(root, file)
            video_name_wo_ext = os.path.splitext(file)[0]

            print(f"Processing: {input_path}")
            process_video(input_path, video_name_wo_ext)

print("✅ All videos processed. Outputs saved to:")
print(f"📁 CSVs: {csv_folder}")
print(f"📁 Line plots: {line_plot_folder}")
print(f"📁 Histograms: {histogram_folder}")
