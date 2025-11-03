import cv2
import os
import tifffile as tiff
import numpy as np

# Define the input directory containing files (Modify this path as needed)
input_dir = r'Video file folder path'

# Dynamically create an output directory with the same structure
base_input_folder_name = os.path.basename(os.path.normpath(input_dir))  # Get input folder name
output_base_dir = os.path.join(r'C:/Users/Admin/Desktop/New 2/Water on soap/20250422', base_input_folder_name)

# Ensure the base output directory exists
os.makedirs(output_base_dir, exist_ok=True)

# Supported file extensions
video_extensions = ['.mp4', '.avi', '.mkv', '.cine', '.mov', '.wmv', '.flv', '.m4v']
tiff_extensions = ['.tif', '.tiff']

# Ask once whether to rotate all videos
rotate_all = input("Rotate all videos 90° clockwise? (y/n): ").strip().lower() == 'y'

# Walk through the input directory, including subfolders
for root, _, files in os.walk(input_dir):
    for file_name in files:
        input_path = os.path.join(root, file_name)

        # Get the file extension
        file_extension = os.path.splitext(file_name)[1].lower()

        # Create a mirrored folder structure in the output directory
        relative_path = os.path.relpath(root, input_dir)  # Get relative path from base folder
        output_dir = os.path.join(output_base_dir, relative_path)
        os.makedirs(output_dir, exist_ok=True)  # Create subfolder if needed

        # Generate output file name and path
        input_base_name = os.path.splitext(file_name)[0]
        output_file_name = f"{input_base_name}_converted.avi"
        output_path = os.path.join(output_dir, output_file_name)

        if file_extension in tiff_extensions:
            # Handle TIFF to AVI conversion
            try:
                with tiff.TiffFile(input_path) as tiff_file:
                    first_frame = tiff_file.pages[0].asarray()
                    height, width = first_frame.shape if len(first_frame.shape) == 2 else first_frame.shape[:2]
                    fps = 60  # Define FPS manually

                    # Swap width & height if rotating
                    output_size = (height, width) if rotate_all else (width, height)

                    # Define codec and create VideoWriter
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                    out = cv2.VideoWriter(output_path, fourcc, fps, output_size)

                    for page in tiff_file.pages:
                        frame = page.asarray()
                        if frame.dtype != np.uint8:
                            frame = (frame / frame.max() * 255).astype(np.uint8)  # Normalize to 0–255
                        if len(frame.shape) == 2:
                            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                        if rotate_all:
                            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                        out.write(frame)

                    out.release()
                    print(f"✅ TIFF Converted {'and rotated ' if rotate_all else ''}: {output_file_name}")

            except Exception as e:
                print(f"❌ Error processing TIFF {file_name}: {e}")

        elif file_extension in video_extensions:
            # Handle video file conversion
            try:
                cap = cv2.VideoCapture(input_path)

                if not cap.isOpened():
                    print(f"🚨 Failed to open video file: {file_name}")
                    continue

                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS) or 60  # Use detected FPS or default to 60

                output_size = (height, width) if rotate_all else (width, height)

                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(output_path, fourcc, fps, output_size)

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if rotate_all:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                    out.write(frame)

                cap.release()
                out.release()
                print(f"✅ Video Converted {'and rotated ' if rotate_all else ''}: {output_file_name}")

            except Exception as e:
                print(f"❌ Error processing video {file_name}: {e}")

        else:
            print(f"⚠️ Skipping unsupported file: {file_name}")

print(f"\n Batch processing completed! Converted files saved in: {output_base_dir}")
