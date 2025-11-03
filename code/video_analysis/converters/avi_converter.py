import cv2
import os
import tifffile as tiff
import numpy as np

# Define the input file path
input_path = r'Video file path'

# Dynamically generate the output file name based on the input file name
input_file_name = os.path.splitext(os.path.basename(input_path))[0]  # Extract base name
output_file_name = f"{input_file_name}_converted"  # Add a suffix or modify as needed

# Define the output directory and combine it with the file name + extension
output_dir = r'C:/Users/Admin/Desktop/New 2'
os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
output_path = os.path.join(output_dir, f"{output_file_name}.avi")

# Check the input file type
file_extension = os.path.splitext(input_path)[1].lower()

if file_extension in ['.tif', '.tiff']:
    # Handle TIFF to AVI conversion
    with tiff.TiffFile(input_path) as tiff_file:
        # Get frame dimensions
        first_frame = tiff_file.pages[0].asarray()
        height, width = first_frame.shape if len(first_frame.shape) == 2 else first_frame.shape[:2]
        fps = 60  # Define FPS manually

        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec for AVI format
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process each frame
        for page in tiff_file.pages:
            frame = page.asarray()  # Load frame
            if frame.dtype != np.uint8:
                frame = (frame / frame.max() * 255).astype(np.uint8)  # Normalize to 0–255
            if len(frame.shape) == 2:  # Grayscale to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            out.write(frame)

        # Release resources
        out.release()
        print(f"TIFF to AVI conversion completed. Output saved at: {output_path}")

elif file_extension in ['.mp4', '.avi', '.mkv', '.cine', '.mov', '.wmv', '.flv', '.m4v']:
    # Handle video file conversion
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print(f"Failed to open video file: {input_path}")
    else:
        # Get frame dimensions and frame rate
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 60
        # fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Use FPS from input or default to 30

        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec for AVI format (MJPG)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Read and write each frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        # Release resources
        cap.release()
        out.release()
        print(f"Video file conversion completed. Output saved at: {output_path}")

else:
    print(f"Unsupported file format: {file_extension}")