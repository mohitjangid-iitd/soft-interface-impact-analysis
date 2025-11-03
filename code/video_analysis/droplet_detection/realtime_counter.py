import cv2
import numpy as np
import matplotlib.pyplot as plt
from Functions import crop  # Self-defined
import pandas as pd

Scale = 96 #mm

fps = 500

rec = cv2.VideoCapture(r'Video file path')  # Start video capture

rec.set(cv2.CAP_PROP_POS_FRAMES,0)

obj_det = cv2.createBackgroundSubtractorMOG2(varThreshold=16)  # Separate moving objects from background

all_radii = []  # List to store all radii
drop_count = 0  # Counter for drops
frame_no = 0
cross_time = []
coordinates_and_time = []

line_position = 60  # Y-coordinate of the counting line within the ROI (adjust based on your ROI)
min_contour_area = 1100  # Minimum contour area to be considered a drop
max_contour_area = 2500  # Maximum contour area to be considered a drop
previous_centroids = []  # Store centroids from the previous frame

paused = False  # Add a flag to track whether the video is paused or not

while True:
    if not paused:  # Only read a new frame if not paused
        ret, frame = rec.read()  # Frame-by-frame analysis of a given video or live feed
        if not ret:  # If video ends, break the loop
            break
        
        frame_no += 1
        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Adjust the scale ratio
        ratio = Scale / int(rec.get(3))  # mm/pix (BY ImageJ)
        
        # Adjust ROI after rotation (consider the new coordinates due to rotation)
        roi = crop(frame, 0.30, 0.33, 0.38, 0.08)  # Adjusted cropping for rotated frame
        
        mask = obj_det.apply(roi)  # Apply background subtraction
        
        # Apply manual thresholding on mask
        _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area = 0
        radii = []
        current_centroids = []  # Store centroids for the current frame
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if min_contour_area < area < max_contour_area:  # Filter based on area
                M = cv2.moments(cnt)
                if M['m00'] != 0:  # If area is != zero
                    cx = int(M['m10'] / M['m00'])  # Centroid x-coordinate within the ROI
                    cy = int(M['m01'] / M['m00'])  # Centroid y-coordinate within the ROI
                    
                    current_centroids.append((cx, cy))
                    
                    # Check if the drop crosses the counting line within the ROI
                    for (prev_cx, prev_cy) in previous_centroids:
                        if prev_cy < line_position <= cy:  # Drop crosses the line from above
                            drop_count += 1
                            cross_time.append(frame_no / fps)
                            break
                
                # Draw contours on the ROI
                cv2.drawContours(roi, [cnt], -1, (8, 255, 0), -1)
                total_area += area
                
                # Calculate the radius if the contour is large enough to be a drop
                radius = np.sqrt(area / np.pi)
                radii.append(radius)
                all_radii.append(radius)  # Collecting radii for final mean calculation
                coordinates_and_time.append([cy*ratio ,frame_no/fps ])
                cv2.line(roi,(0,cy),(roi.shape[1], cy), (0, 0, 255), 2)
                cv2.putText(frame, f'Dis. : {cy*ratio}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
        # Update centroids for the next frame
        previous_centroids = current_centroids
        
        # Calculate the average radius for the current frame
        avg_radius = np.mean(radii) if radii else 0
        
        # Draw the counting line within the ROI
        cv2.line(roi, (0, line_position), (roi.shape[1], line_position), (0, 0, 255), 2)
        
        # Display information on the main frame
        cv2.putText(frame, f'Total Area: {total_area}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Avg Radius: {avg_radius:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Drop Count: {drop_count}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Frame no. : {frame_no}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        frame = cv2.resize(frame, (0, 0), fx=.5, fy=.5)
        # Show the frames
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)
        cv2.imshow('ROI', roi)
    
    key = cv2.waitKey(1) & 0xFF  # Capture key press
    
    if key == ord('c'):  # Press 'c' to break the loop
        break
    elif key == ord('p'):  # Press 'p' to pause or resume
        paused = not paused  # Toggle the paused state

# Scaling radii based on the ratio
all_radii_scaled = np.array(all_radii) * ratio

rec.release()  # Release the video capture (Camera off)
cv2.destroyAllWindows()  # Close all windows

# data = [coord + [count] for coord, count in zip(coordinates_and_time, drop_count)]
# df = pd.DataFrame(data, columns=['Y-coordinate(mm)', 'Time(Sec)', 'Drop Count'])
df = pd.DataFrame(coordinates_and_time, columns=['Y-coordinate(mm)', 'Time(Sec)'])
df.to_csv('0_mlpmin_below.csv', index=False, float_format='%.4f')

# Calculate the final mean radius after processing the entire video
final_mean_radius = np.mean(all_radii) if all_radii else 0
print(f'Final Mean Radius: {final_mean_radius * ratio:.2f} mm')
print(f'Total Drop Count: {drop_count}')
print(f'Time Interval: {cross_time}')
print(f'Time difference between consecutive drops: {np.diff(cross_time)}')

# Plotting the histogram for drop radii
plt.figure()
plt.hist(all_radii_scaled, bins=100, density=True, alpha=.6, color='g', range=(0.8, 1.8))
plt.xlabel('Drop Radius (mm)')
plt.ylabel('Density')
plt.title('Histogram of Drop Radii')
plt.axvline(x=final_mean_radius * ratio, color='r', linestyle='-')
plt.show()

# Plotting the histogram for drop time diff.
plt.figure()
plt.hist(np.diff(cross_time), alpha=.6, bins=100)
plt.xlabel('Time interval between two consecutive drops (s)')
plt.ylabel('Density')
plt.title('Histogram of Drop Time Differences')
plt.show()