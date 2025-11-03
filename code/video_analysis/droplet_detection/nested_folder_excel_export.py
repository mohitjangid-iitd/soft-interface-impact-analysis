import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from Functions import crop  # Ensure you have the crop function defined in Functions.py

# Function to process a single video
def process_video(video_path, output_folder, scale=96, fps=500):
    video_name = os.path.splitext(os.path.basename(video_path))[0]  # Extract video name

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize video capture
    rec = cv2.VideoCapture(video_path)
    rec.set(cv2.CAP_PROP_POS_FRAMES, 0)

    obj_det = cv2.createBackgroundSubtractorMOG2(varThreshold=16)  # Background subtraction

    all_radii = []  
    drop_count = 0  
    frame_no = 0
    cross_time = []
    coordinates_and_time = []
    
    paused = False  

    line_position = 60  
    min_contour_area = 100  
    max_contour_area = 750  
    previous_centroids = []  

    while True:
        if not paused:  
            ret, frame = rec.read()
            if not ret:  
                break

            frame_no += 1

            # Rotate the frame 90 degrees clockwise
            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            # Adjust the scale ratio
            ratio = scale / int(rec.get(4))  

            # Adjust ROI after rotation
            roi = crop(frame, 0.30, 0.5, 0.38, 0.48)  

            mask = obj_det.apply(roi)  

            # Apply manual thresholding
            _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

            # Apply morphological operations
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            total_area = 0
            radii = []
            current_centroids = []  

            for cnt in contours:
                area = cv2.contourArea(cnt)

                if min_contour_area < area < max_contour_area:  
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:  
                        cx = int(M['m10'] / M['m00'])  
                        cy = int(M['m01'] / M['m00'])  

                        current_centroids.append((cx, cy))

                        for (prev_cx, prev_cy) in previous_centroids:
                            if prev_cy < line_position <= cy:  
                                drop_count += 1
                                cross_time.append(frame_no / fps)
                                break

                    # Draw contours on the ROI
                    cv2.drawContours(roi, [cnt], -1, (8, 255, 0), -1)
                    total_area += area

                    # Calculate radius
                    radius = np.sqrt(area / np.pi)
                    radii.append(radius)
                    all_radii.append(radius)  
                    coordinates_and_time.append([cy * ratio, frame_no / fps, radius * ratio])

                    # Draw a line at detected drop location
                    cv2.line(roi, (0, cy), (roi.shape[1], cy), (0, 0, 255), 2)
                    cv2.putText(frame, f'Dis. : {cy*ratio:.2f} mm', (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            previous_centroids = current_centroids

            avg_radius = np.mean(radii) if radii else 0

            # Draw counting line
            cv2.line(roi, (0, line_position), (roi.shape[1], line_position), (0, 0, 255), 2)

            # Display text on video
            cv2.putText(frame, f'Total Area: {total_area}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Avg Radius: {avg_radius:.2f} mm', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Drop Count: {drop_count}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Frame No.: {frame_no}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        frame_resized = cv2.resize(frame, (400, 600))

        cv2.imshow(video_name, frame_resized)
        cv2.imshow('Processed Mask', mask)
        cv2.imshow('ROI', roi)

        key = cv2.waitKey(1) & 0xFF  
        if key == ord('c'):  
            break
        elif key == ord('p'):  
            paused = not paused  

    rec.release()
    cv2.destroyAllWindows()  

    # Scaling radii
    all_radii_scaled = np.array(all_radii) * ratio

    # Save CSV
    csv_file_path = os.path.join(output_folder, f"{video_name}_results.csv")
    df = pd.DataFrame(coordinates_and_time, columns=['Y-coordinate(mm)', 'Time(Sec)', 'Radius(mm)'])
    df.to_csv(csv_file_path, index=False, float_format='%.4f')

    print(f"Processed {video_path}")
    print(f"Results saved at {csv_file_path}")

    # Save Histogram
    plt.figure()
    plt.hist(all_radii_scaled, bins=100, density=True, alpha=0.6, color='g')
    plt.xlabel('Drop Radius (mm)')
    plt.ylabel('Density')
    plt.title('Histogram of Drop Radii')
    plt.axvline(x=np.mean(all_radii_scaled), color='r', linestyle='-')
    radius_hist_path = os.path.join(output_folder, f"{video_name}_radius_histogram.png")
    plt.savefig(radius_hist_path)
    plt.close()


# Function to process videos in folders
def process_videos_in_folders(input_folder):
    for root_dir, sub_dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".avi"):  
                video_path = os.path.join(root_dir, file)
                relative_path = os.path.relpath(root_dir, input_folder)
                output_folder = os.path.join(input_folder + "_results", relative_path)
                process_video(video_path=video_path, output_folder=output_folder)

# Main execution
if __name__ == "__main__":
    input_folder_path = r"Input folder path"  
    process_videos_in_folders(input_folder=input_folder_path)
