import cv2
import numpy as np
import pandas as pd
import os
from Functions import crop  # Importing your custom function

# Set parameters
video_path = r'input video path'  
output_folder = r'output folder name'
os.makedirs(output_folder, exist_ok=True)

Scale = 96  # mm
fps = 500

# Define frame range
start_frame = 1
end_frame = 4852

# Open video
rec = cv2.VideoCapture(video_path)
rec.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

# Scaling ratio
frame_width = int(rec.get(4))
if frame_width == 0:
    print("Error: Could not read video properties.")
    exit()
ratio = Scale / frame_width  # mm/pixel

# Background subtractor
obj_det = cv2.createBackgroundSubtractorMOG2(varThreshold=16)

# Drop detection settings
line_position = 60  
min_contour_area = 1100
max_contour_area = 3000

drop_data = []
frame_no = start_frame
drop_count = 0
previous_centroids = []

while frame_no <= end_frame:
    ret, frame = rec.read()
    if not ret:
        break

    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  

    # Use the familiar cropping function from v3pt0.py
    roi = crop(frame, 0.44, 0.32, 0.15, 0.65)

    mask = obj_det.apply(roi)
    _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    current_centroids = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if min_contour_area < area < max_contour_area:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])  
                cy = int(M['m01'] / M['m00'])  
                current_centroids.append((cx, cy))

                # Check for drop crossing line
                for (prev_cx, prev_cy) in previous_centroids:
                    if prev_cy < line_position <= cy:
                        drop_count += 1
                        break

                # **Fit Ellipse (Only if Contour has Enough Points)**
                if len(cnt) >= 5:
                    ellipse = cv2.fitEllipse(cnt)
                    (xc, yc), (major_axis, minor_axis), angle = ellipse

                    # Convert to mm
                    xc_mm, yc_mm = xc * ratio, yc * ratio
                    major_axis_mm = major_axis * ratio
                    minor_axis_mm = minor_axis * ratio

                    # **Draw Ellipse**
                    cv2.ellipse(roi, ellipse, (255, 0, 0), 2)

                    # **Get Bounding Box to Crop the Drop**
                    x, y, w, h = cv2.boundingRect(cnt)

                    # **Ensure bounding box is within image limits**
                    x, y = max(0, x), max(0, y)
                    w, h = min(roi.shape[1] - x, w), min(roi.shape[0] - y, h)

                    # **Save Drop Image**
                    drop_crop = roi[y:y+h, x:x+w].copy()
                    drop_filename = os.path.join(output_folder, f'drop_frame{frame_no}.png')
                    cv2.imwrite(drop_filename, drop_crop)

                    # **Save Drop Data**
                    drop_data.append([
                        frame_no, frame_no / fps, xc_mm, yc_mm, major_axis_mm, minor_axis_mm, angle
                    ])

    previous_centroids = current_centroids

    # Display
    cv2.imshow('Video', cv2.resize(frame, (0, 0), fx=0.5, fy=0.5))
    cv2.imshow('Mask', mask)
    cv2.imshow('ROI', roi)

    frame_no += 1  

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

rec.release()
cv2.destroyAllWindows()

# Save Data
df_ellipses = pd.DataFrame(drop_data, columns=[
    'Frame', 'Time(s)', 'X (mm)', 'Y (mm)', 'Major Axis (mm)', 'Minor Axis (mm)', 'Angle (deg)'
])
df_ellipses.to_csv(r'C:/Users/Admin/Desktop/1pt06_4mlpmin/1stdrop_ellipses.csv', index=False, float_format='%.4f')

print(f"Processing completed! {len(drop_data)} drops detected. Data saved in 'drop_ellipses.csv'.")