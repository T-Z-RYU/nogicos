import os
import json
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess


def create_video_from_screenshots(
    directory_path, output_file="output.mp4", fps=1, font_size=36
):
    """
    Creates a video from screenshot files in a directory, with the task name at the top.

    Args:
        directory_path: Path to the directory containing screenshots and task.json
        output_file: Name of the output video file
        fps: Frames per second (default: 1 second per screenshot)
        font_size: Font size for the task name text
    """
    # Get task name from task.json
    task_path = os.path.join(directory_path, "task.json")
    if not os.path.exists(task_path):
        raise FileNotFoundError(f"task.json not found in {directory_path}")

    with open(task_path, "r") as f:
        task_data = json.load(f)

    # Determine task name based on task type
    if task_data.get("type") == "explore":
        task_name = task_data.get("task", "Unknown Task")
    elif task_data.get("type") == "test":
        task_name = f"Test the function {task_data.get('function_name', '')}"
    else:
        task_name = "Unknown Task"

    # Get all screenshot files, sorted by index
    screenshot_pattern = os.path.join(directory_path, "*_state_screenshot.png")
    screenshot_files = sorted(glob.glob(screenshot_pattern))

    if not screenshot_files:
        raise FileNotFoundError(f"No screenshot files found in {directory_path}")

    # Get dimensions from first image
    first_img = cv2.imread(screenshot_files[0])
    height, width, _ = first_img.shape

    # Create temporary directory for annotated frames
    temp_dir = os.path.join(directory_path, "temp_frames")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Process each screenshot
        annotated_files = []
        for i, screenshot_file in enumerate(screenshot_files):
            # Open the image with PIL for text rendering
            img = Image.open(screenshot_file)
            draw = ImageDraw.Draw(img)

            # Try to load a system font
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except IOError:
                    # Fallback to default
                    font = ImageFont.load_default()

            # Add black background for text visibility
            text_bg_height = font_size + 20
            draw.rectangle([(0, 0), (img.width, text_bg_height)], fill="black")

            # Add task name text
            text_width = draw.textlength(task_name, font=font)
            text_x = (img.width - text_width) // 2
            draw.text((text_x, 10), task_name, font=font, fill="white")

            # Save the annotated frame
            temp_file = os.path.join(temp_dir, f"frame_{i:03d}.png")
            img.save(temp_file)
            annotated_files.append(temp_file)

        # Use ffmpeg to create the video
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            os.path.join(temp_dir, "frame_%03d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "23",
            output_file,
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Video created successfully: {output_file}")

    finally:
        # Clean up temporary files
        for file in annotated_files:
            try:
                os.remove(file)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass


def process_multiple_directories(base_directory, output_dir=None):
    """
    Process multiple directories and create videos for each

    Args:
        base_directory: Directory containing multiple task directories
        output_dir: Directory to save the output videos (default: same as base_directory)
    """
    if output_dir is None:
        output_dir = base_directory

    os.makedirs(output_dir, exist_ok=True)

    # Find all directories that contain task.json
    for root, dirs, files in os.walk(base_directory):
        if "task.json" in files and any(
            "_state_screenshot.png" in file for file in files
        ):
            # Get directory name
            dir_name = os.path.basename(root)
            output_file = os.path.join(output_dir, f"{dir_name}_video.mp4")

            try:
                print(f"Processing directory: {root}")
                create_video_from_screenshots(root, output_file)
            except Exception as e:
                print(f"Error processing {root}: {e}")


# Example usage:
if __name__ == "__main__":
    # Process a single directory
    # create_video_from_screenshots("/path/to/specific/directory")

    # Or process multiple directories
    process_multiple_directories("../drugs", output_dir="./drugs_videos")
