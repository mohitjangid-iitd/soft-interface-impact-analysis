import cv2
import numpy as np
import pandas as pd
import os  # For extracting file name and directory
from Functions import crop  # Self-defined function

# Parameters
Scale = 96  # mm
fps = 500 # Frames per second

# Video input
video_path = r'Input video path'
rec = cv2.VideoCapture(video_path)
rec.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Generate output CSV file name based on input video name and directory
input_filename = os.path.basename(video_path)  # Extract the file name
output_filename = os.path.splitext(input_filename)[0] + '_time.csv'  # Append suffix and .csv
output_directory = os.path.dirname(video_path)  # Extract the input file's directory
output_csv_path = os.path.join(output_directory, output_filename)  # Combine directory and file name

# Background subtractor
obj_det = cv2.createBackgroundSubtractorMOG2(varThreshold=16)

# Counting line and contour area range
line_position = 150  # Y-coordinate for counting line
min_contour_area = 500
max_contour_area = 3500

# Data storage
drop_count = 0
frame_no = 0
cross_time = []  # Times when drops cross the line
coordinates_and_time_radious = []  # Store Y-coordinate and time when drops cross the line

previous_centroids = []  # Centroids from the previous frame
paused = False  # Video pause state

# Video processing loop
while True:
    if not paused:
        ret, frame = rec.read()
        if not ret:  # End of video
            break

        frame_no += 1
        # Scale ratio for mm/pixel
        ratio = Scale / int(rec.get(3))  # mm/pixel (BY ImageJ)

        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Crop the ROI
        roi = crop(frame, 0.30, 0.53, 0.38, 0.3)

        # Background subtraction and thresholding
        mask = obj_det.apply(roi)
        _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        current_centroids = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            Radious = np.sqrt(area/np.pi)*ratio
            if min_contour_area < area < max_contour_area:  # Filter based on area
                M = cv2.moments(cnt)
                if M['m00'] != 0:  # Avoid division by zero
                    cx = int(M['m10'] / M['m00'])  # Centroid X
                    cy = int(M['m01'] / M['m00'])  # Centroid Y
                    current_centroids.append((cx, cy))
                    cv2.circle(roi, (cx,cy), 4, (255,0,255),-1)
                    # Check if drop crosses the counting line
                    for (_, prev_cy) in previous_centroids:
                        if prev_cy < line_position <= cy:  # Crosses line
                            drop_count += 1
                            time_at_crossing = frame_no / fps  # Time in seconds
                            cross_time.append(time_at_crossing)
                            
                            coordinates_and_time_radious.append([cx * ratio, cy * ratio, time_at_crossing, Radious])
                            break  # Stop further checks for this drop

        # Update centroids for the next frame
        previous_centroids = current_centroids

        # Draw the counting line on the ROI
        cv2.line(roi, (0, line_position), (roi.shape[1], line_position), (0, 0, 255), 2)
        
        # Display the video and mask
        cv2.putText(frame, f'Drop Count: {drop_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Frame no: {frame_no}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Frame', cv2.resize(frame, (0, 0), fx=0.5, fy=0.5))  # Resize for display
        cv2.imshow('Mask', mask)
        cv2.imshow('ROI', roi)

    # Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):  # Press 'c' to exit
        break
    elif key == ord('p'):  # Press 'p' to pause/resume
        paused = not paused  # Toggle pause state

# Release resources
rec.release()
cv2.destroyAllWindows()

# # Save the data to CSV
# df = pd.DataFrame(coordinates_and_time_radious, columns=['X-coordinate(mm)','Y-coordinate(mm)', 'Time(Sec)', 'Radious(mm)'])
# df.to_csv(output_csv_path, index=False, float_format='%.4f')

# Output results
print(f'Total Drop Count: {drop_count}')
print(f'Data saved to: {output_csv_path}')