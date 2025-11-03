import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the CSV file
file_path = r"CSV path"
df = pd.read_csv(file_path)

# Define column names
drop_col = "Drop number"
angle_col = "Angle (deg)"

# Select drop range
drop_range = (1, 37)  # Adjust as needed

# Filter selected drops
filtered_df = df[df[drop_col].between(drop_range[0], drop_range[1])]

# Create a new folder to save histograms
save_folder = r"C:/Users/Admin/Desktop/angle_histograms"
os.makedirs(save_folder, exist_ok=True)  # Create folder if it doesn't exist

# Plot and save histogram for each drop
for drop_no, group in filtered_df.groupby(drop_col):
    plt.figure(figsize=(8, 6))
    plt.hist(group[angle_col], bins=30, alpha=0.7, color='steelblue')
    plt.xlabel("Angle (degrees)", fontsize='large')
    plt.ylabel("Probability Density", fontsize='large')
    plt.title(f"Angle Histogram - Drop {drop_no}", fontsize=20)
    plt.grid(True)
    plt.tight_layout()
    # plt.show()
    
    # Save the figure
    # save_path = os.path.join(save_folder, f"drop_{drop_no}_angle_histogram.png")
    # plt.savefig(save_path)
    plt.close()  # Close the figure to avoid too many open plots


# If you want to save a **combined histogram** (all drops together), use this:
plt.figure(figsize=(10, 6))
plt.hist(filtered_df[angle_col],density=True, bins=60, alpha=0.7, color='orchid')
plt.xlabel("Angle (degrees)", fontsize='large')
plt.ylabel("Probability Density", fontsize='large')
plt.title("Ellipse Angle Histogram", fontsize=24)
# plt.grid(True)
plt.tight_layout()
plt.show()
# combined_save_path = os.path.join(save_folder, "combined_angle_histogram.png")
# plt.savefig(combined_save_path)
plt.close()
