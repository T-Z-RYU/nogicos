import os
import sys
import zipfile
import subprocess
import urllib.request
import shutil

VIDEO_PATH = os.path.join("video_analysis", "ivy_social_account.mp4")
OUTPUT_DIR = os.path.join("video_analysis", "frames")
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_EXE = "ffmpeg.exe"

def download_ffmpeg():
    if os.path.exists(FFMPEG_EXE):
        print("Found ffmpeg.exe, skipping download.")
        return

    print(f"Downloading FFmpeg from {FFMPEG_URL}...")
    zip_path = "ffmpeg.zip"
    try:
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
        print("Download complete. Extracting...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the ffmpeg.exe path inside the zip
            ffmpeg_path_in_zip = None
            for file in zip_ref.namelist():
                if file.endswith("bin/ffmpeg.exe"):
                    ffmpeg_path_in_zip = file
                    break
            
            if ffmpeg_path_in_zip:
                # Extract only ffmpeg.exe
                source = zip_ref.open(ffmpeg_path_in_zip)
                target = open(FFMPEG_EXE, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                print("ffmpeg.exe extracted.")
            else:
                print("Error: ffmpeg.exe not found in the zip file.")
                sys.exit(1)
                
    except Exception as e:
        print(f"Error downloading or extracting FFmpeg: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

def extract_frames():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Check if video exists
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file not found at {VIDEO_PATH}")
        sys.exit(1)

    print("Starting frame extraction (1 frame per second)...")
    # Command: ffmpeg -i video.mp4 -vf fps=1 frames/frame_%04d.png
    cmd = [
        os.path.abspath(FFMPEG_EXE),
        "-i", os.path.abspath(VIDEO_PATH),
        "-vf", "fps=1",
        os.path.join(os.path.abspath(OUTPUT_DIR), "frame_%04d.png"),
        "-y" # Overwrite output files
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Frames extracted to {OUTPUT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")

if __name__ == "__main__":
    download_ffmpeg()
    extract_frames()

