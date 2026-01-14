"""
This script creates 4x4 montages from exploration videos. It's made for the purposes of the demo.
"""

import subprocess
import sys
import os
import random


def get_video_duration(input_file):
    """
    Uses ffprobe to determine the duration of the input video.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_file,
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        duration = float(result.stdout.strip())
        return duration
    except ValueError:
        print("Could not determine video duration.")
        sys.exit(1)


def sample_start_times(video_duration, segment_duration, num_segments):
    """
    Randomly samples non-overlapping start times.

    The algorithm generates 16 random numbers in the interval
    [0, video_duration - num_segments * segment_duration],
    sorts them, and then shifts each by i * segment_duration.
    This ensures that the segments do not overlap.
    """
    if video_duration < num_segments * segment_duration:
        print(
            "Video is too short to extract the desired number of non-overlapping segments."
        )
        sys.exit(1)

    # Generate sorted random offsets
    random_offsets = sorted(
        random.uniform(0, video_duration - num_segments * segment_duration)
        for _ in range(num_segments)
    )
    start_times = [
        random_offsets[i] + i * segment_duration for i in range(num_segments)
    ]
    return start_times


def extract_segments(input_file, segment_duration=180, num_segments=16):
    """
    Extracts segments from random non-overlapping portions of the input video.

    Each segment is sped up by 10x and scaled down to 1/4 of the original size.
    """
    video_duration = get_video_duration(input_file)
    print(f"Video duration: {video_duration:.2f} seconds")
    start_times = sample_start_times(video_duration, segment_duration, num_segments)
    print("Random start times (non-overlapping):", [f"{st:.2f}" for st in start_times])

    for i, start_time in enumerate(start_times):
        output_file = f"seg{i}.mp4"
        # ffmpeg command:
        #   -ss: Seek to start_time.
        #   -t: Extract segment_duration seconds.
        #   -vf: Apply two filters:
        #         setpts=PTS/10 speeds up video by 10x,
        #         scale=iw/4:ih/4 scales the video down to 1/4 of its width and height.
        #   -an: Remove audio.
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-t",
            str(segment_duration),
            "-i",
            input_file,
            "-vf",
            "setpts=PTS/20,scale=iw/4:ih/4",
            "-an",
            output_file,
        ]
        print(
            f"Extracting segment {i} starting at {start_time:.2f}s to {output_file}..."
        )
        subprocess.run(cmd, check=True)


def combine_segments(num_segments=16, output_file="output.mp4"):
    """
    Combines the 16 segments (seg0.mp4 ... seg15.mp4) into a 4x4 grid.

    This is accomplished by first stacking four segments horizontally to form rows,
    and then stacking these rows vertically.
    """
    inputs = []
    for i in range(num_segments):
        inputs.extend(["-i", f"seg{i}.mp4"])

    if num_segments == 16:
        filter_complex = (
            "[0:v][1:v][2:v][3:v]hstack=inputs=4[row0];"
            "[4:v][5:v][6:v][7:v]hstack=inputs=4[row1];"
            "[8:v][9:v][10:v][11:v]hstack=inputs=4[row2];"
            "[12:v][13:v][14:v][15:v]hstack=inputs=4[row3];"
            "[row0][row1][row2][row3]vstack=inputs=4"
        )
    elif num_segments == 4:
        # 2x2 version
        filter_complex = (
            "[0:v][1:v]hstack=inputs=2[row0];"
            "[2:v][3:v]hstack=inputs=2[row1];"
            "[row0][row1]vstack=inputs=2"
        )
    elif num_segments == 9:
        # 3x3 version
        filter_complex = (
            "[0:v][1:v][2:v]hstack=inputs=3[row0];"
            "[3:v][4:v][5:v]hstack=inputs=3[row1];"
            "[6:v][7:v][8:v]hstack=inputs=3[row2];"
            "[row0][row1][row2]vstack=inputs=3"
        )

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex",
            filter_complex,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "veryfast",
            output_file,
        ]
    )

    print("Combining segments into a 4x4 grid...")
    subprocess.run(cmd, check=True)
    print(f"Output video saved as {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py input_video.mp4")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        sys.exit(1)

    # Extract segments from random non-overlapping portions of the input video
    num_segments = 9
    segment_duration = 360
    extract_segments(input_file, segment_duration, num_segments)

    # Combine the segments into a grid
    combine_segments(num_segments)


if __name__ == "__main__":
    main()
