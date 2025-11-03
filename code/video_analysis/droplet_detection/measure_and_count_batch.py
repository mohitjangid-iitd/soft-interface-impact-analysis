import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from Functions import crop  # Self-defined

Scale = 237  # mm

video_folder = r'Input folder path'  # Path to the folder containing videos
video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]  # List all .mp4 files

obj_det = cv2.createBackgroundSubtractorMOG2(varThreshold=16)  # Object detector

line_position = 60  # Y-coordinate of the counting line
min_contour_area = 100  # Minimum contour area for a drop
max_contour_area = 500  # Maximum contour area for a drop

# Function to process each video
def process_video(video_path):
    rec = cv2.VideoCapture(video_path)  # Open video file
    
    all_radii = []  # Store all drop radii
    drop_count = 0  # Counter for drops
    previous_centroids = []  # Store centroids from the previous frame

    while True:
        ret, frame = rec.read()  # Read frame-by-frame
        if not ret:  # If video ends, break the loop
            break

        ratio = Scale / int(rec.get(4))  # mm/pixel
        
        roi = crop(frame, 0.4, 0.3, 0.3, 0.1)  # Crop region of interest
        
        mask = obj_det.apply(roi)  # Background subtraction
        
        _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)  # Thresholding
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Morphological operations
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Find contours

        total_area = 0
        radii = []
        current_centroids = []  # Store current frame centroids

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if min_contour_area < area < max_contour_area:  # Filter drops by area
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])  # Centroid x-coordinate
                    cy = int(M['m01'] / M['m00'])  # Centroid y-coordinate
                    current_centroids.append((cx, cy))

                    # Check if the drop crosses the counting line
                    for (prev_cx, prev_cy) in previous_centroids:
                        if prev_cy < line_position <= cy:  # Drop crosses the line from above
                            drop_count += 1
                            break

                cv2.drawContours(roi, [cnt], -1, (8, 255, 0), -1)
                total_area += area

                # Calculate the radius
                radius = np.sqrt(area / np.pi)
                radii.append(radius)
                all_radii.append(radius)

        previous_centroids = current_centroids  # Update centroids

        avg_radius = np.mean(radii) if radii else 0

        # Draw the counting line
        cv2.line(roi, (0, line_position), (roi.shape[1], line_position), (0, 0, 255), 2)

        # Display the frame and mask (optional)
        cv2.putText(frame, f'Total Area: {total_area}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Avg Radius: {avg_radius:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Drop Count: {drop_count}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)
        cv2.imshow('ROI', roi)

        if cv2.waitKey(1) == ord('c'):  # Break loop if 'c' is pressed
            break

    rec.release()  # Release video
    cv2.destroyAllWindows()  # Close windows

    # Scale all radii
    all_radii_scaled = np.array(all_radii) * ratio

    # Final mean radius calculation
    final_mean_radius = np.mean(all_radii) if all_radii else 0

    print(f'Final Mean Radius: {final_mean_radius * ratio:.2f} mm')
    print(f'Total Drop Count: {drop_count}')

    # Plot histogram
    plt.hist(all_radii_scaled, bins=100, density=True, alpha=.6, color='g')
    plt.xlabel('Drop Radius (mm)')
    plt.ylabel('Density')
    plt.title('Histogram of Drop Radii')
    plt.axvline(x=final_mean_radius * ratio, color='r', linestyle='-')
    plt.show()

    # Plot boxplot
    plt.boxplot(all_radii_scaled, vert=False)
    plt.xlabel('Drop Radius (mm)')
    plt.title('Box Plot of Drop Radii')
    plt.show()

# Loop through all videos and process them
for video in video_files:
    video_path = os.path.join(video_folder, video)
    print(f"Processing: {video_path}")
    process_video(video_path)