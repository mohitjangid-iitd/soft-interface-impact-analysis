import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import cv2

# Load CSV
file_path = r"CSV file path"
df = pd.read_csv(file_path)

# Define columns
drop_col = "Drop number"
time_col = "Time(s)"
x_col = "X (mm)"
y_col = "Y (mm)"
major_col = "Major Axis (mm)"
minor_col = "Minor Axis (mm)"
angle_col = "Angle (deg)"

# Select drops
drop_range = (1, 26)
filtered_df = df[df[drop_col].between(drop_range[0], drop_range[1])]

# Compute Reduced Time
filtered_df["Reduced Time (s)"] = filtered_df.groupby(drop_col)[time_col].transform(lambda x: x - x.iloc[0])

# Output folders
output_root = r"C:/Users/Admin/Desktop/1pt04_10mlpmin/drop_videos"
frames_dir = os.path.join(output_root, "frames")
videos_dir = os.path.join(output_root, "videos")

os.makedirs(frames_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)

# Video settings
frame_width = 600
frame_height = 600
fps = 10  # frames per second

# Loop over each drop
for drop_no, group in filtered_df.groupby(drop_col):
    drop_frames_path = os.path.join(frames_dir, f"drop_{drop_no}")
    os.makedirs(drop_frames_path, exist_ok=True)

    print(f"Generating frames for Drop {drop_no}...")

    # Generate and save frames
    for i, (_, row) in enumerate(group.iterrows()):
        fig, ax = plt.subplots(figsize=(6, 6))

        center_x = 0
        center_y = 0
        major_axis = row[major_col]
        minor_axis = row[minor_col]
        angle_deg = row[angle_col]

        # Ellipse
        ellipse = patches.Ellipse(
            (center_x, center_y),
            width=major_axis,
            height=minor_axis,
            angle=angle_deg,
            edgecolor='darkblue',
            facecolor='none',
            linewidth=2
        )
        ax.add_patch(ellipse)

        # Major axis
        angle_rad = np.deg2rad(angle_deg)
        dx_major = (major_axis / 2) * np.cos(angle_rad)
        dy_major = (major_axis / 2) * np.sin(angle_rad)
        ax.plot(
            [center_x - dx_major, center_x + dx_major],
            [center_y - dy_major, center_y + dy_major],
            color='darkblue',
            linewidth=1
        )

        # Minor axis
        dx_minor = (minor_axis / 2) * np.cos(angle_rad + np.pi / 2)
        dy_minor = (minor_axis / 2) * np.sin(angle_rad + np.pi / 2)
        ax.plot(
            [center_x - dx_minor, center_x + dx_minor],
            [center_y - dy_minor, center_y + dy_minor],
            color='darkblue',
            linewidth=1
        )

        # Center point
        ax.plot(center_x, center_y, 'ko', markersize=3)

        # Time label
        ax.set_title(f"Drop {drop_no} — t = {row['Reduced Time (s)']:.3f} s", fontsize=12)

        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.axis('off')

        frame_path = os.path.join(drop_frames_path, f"frame_{i:03d}.png")
        plt.savefig(frame_path, dpi=100)
        plt.close()

    print(f"Creating video for Drop {drop_no}...")

    # Compile video
    video_path = os.path.join(videos_dir, f"drop_{drop_no}_evolution.mp4")
    frame_files = sorted([
        os.path.join(drop_frames_path, f) for f in os.listdir(drop_frames_path)
        if f.endswith(".png")
    ])

    if frame_files:
        # Read one image to get size
        first_frame = cv2.imread(frame_files[0])
        height, width, _ = first_frame.shape
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        for frame_file in frame_files:
            img = cv2.imread(frame_file)
            out.write(img)

        out.release()
        print(f"Saved video for Drop {drop_no} at {video_path}")

print("\n✅ All videos generated successfully!")