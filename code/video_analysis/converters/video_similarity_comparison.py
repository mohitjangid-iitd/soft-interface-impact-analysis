import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Open both videos
cine_cap = cv2.VideoCapture(r'1st video file path')
avi_cap = cv2.VideoCapture(r'2nd video file path')

# Variables to store total SSIM and frame count
total_ssim = 0
frame_count = 0

while True:
    # Read frame from each video
    ret1, frame1 = cine_cap.read()
    ret2, frame2 = avi_cap.read()

    # Break loop if any video ends
    if not ret1 or not ret2:
        break

    # Resize frame2 to match frame1 dimensions, if necessary
    frame2_resized = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))

    # Convert frames to grayscale for SSIM calculation
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2_resized, cv2.COLOR_BGR2GRAY)

    # Calculate SSIM for this frame pair
    ssim_index, _ = ssim(gray1, gray2, full=True, win_size=3)
    total_ssim += ssim_index
    frame_count += 1

    # Optional: print SSIM for each frame
    print(f"Frame {frame_count}: SSIM = {ssim_index}")

# Calculate average SSIM across all frames
average_ssim = total_ssim / frame_count if frame_count > 0 else 0
print(f"Average SSIM across all frames: {average_ssim}")

# Release video capture objects
cine_cap.release()
avi_cap.release()
#0.9830478300686193