import os
import subprocess
import json
import glob
import math
import shutil
import tempfile
from collections import defaultdict


def get_video_duration(video_path):
    """Get the duration of a video in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        video_path,
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def create_concat_file(video_list, output_file):
    """Create a concat file for ffmpeg."""
    with open(output_file, "w") as f:
        for video in video_list:
            f.write(f"file '{os.path.abspath(video)}'\n")


def concatenate_videos(video_list, output_file):
    """Concatenate videos using ffmpeg concat demuxer."""
    temp_concat_file = (
        f"{tempfile.gettempdir()}/concat_{os.path.basename(output_file)}.txt"
    )
    create_concat_file(video_list, temp_concat_file)

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        temp_concat_file,
        "-vf",
        "setpts=PTS/4",
        # "-c",
        # "copy",
        output_file,
    ]
    subprocess.run(cmd, check=True)

    # Clean up
    os.remove(temp_concat_file)

    return output_file


def create_3x3_montage(chunk_videos, output_file, border_size=4):
    """Create a 3x3 montage from 9 videos with black borders."""
    # Create filter complex for 3x3 grid with borders
    inputs = []
    for i in range(9):
        inputs.extend(["-i", chunk_videos[i]])

    # Add padding to each video
    filter_complex = ""
    for i in range(9):
        # Add right and bottom padding to each video
        filter_complex += f"[{i}:v]pad=iw+{border_size}:ih+{border_size}:{border_size}:0:color=black[padded{i}];"

    # Create 3x3 grid
    filter_complex += (
        "[padded0][padded1][padded2]hstack=inputs=3[row0];"
        "[padded3][padded4][padded5]hstack=inputs=3[row1];"
        "[padded6][padded7][padded8]hstack=inputs=3[row2];"
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

    subprocess.run(cmd, check=True)
    return output_file


def process_videos_into_montage(
    base_directory, output_file="final_montage.mp4", border_size=4
):
    """
    Process all screenshot videos, create 9 chunks, and assemble into a 3x3 montage.

    Args:
        base_directory: Directory containing all screenshot videos
        output_file: Final montage output filename
        border_size: Size of black borders between videos (in pixels)
    """
    # Create temp directory for intermediate files
    temp_dir = tempfile.mkdtemp()

    try:
        # Find all videos created from screenshots
        video_pattern = os.path.join(base_directory, "**", "*_video.mp4")
        all_videos = glob.glob(video_pattern, recursive=True)

        if len(all_videos) < 9:
            print(
                f"Warning: Found only {len(all_videos)} videos, need at least 9 for a 3x3 montage"
            )
            if len(all_videos) == 0:
                raise ValueError("No videos found!")

        # Get duration of each video
        video_durations = {}
        total_duration = 0
        for video in all_videos:
            duration = get_video_duration(video)
            video_durations[video] = duration
            total_duration += duration

        # Calculate target duration for each chunk
        target_chunk_duration = total_duration / 9
        print(f"Total video duration: {total_duration:.2f} seconds")
        print(f"Target duration per chunk: {target_chunk_duration:.2f} seconds")

        # Group videos into 9 chunks of approximately equal duration
        chunks = [[] for _ in range(9)]
        chunk_durations = [0] * 9

        # Sort videos by duration (longest first for better distribution)
        sorted_videos = sorted(
            video_durations.items(), key=lambda x: x[1], reverse=True
        )

        # First pass - assign longest videos to chunks
        for video, duration in sorted_videos:
            # Find the chunk with the shortest duration
            shortest_chunk_idx = chunk_durations.index(min(chunk_durations))
            chunks[shortest_chunk_idx].append(video)
            chunk_durations[shortest_chunk_idx] += duration

        # Create the 9 chunk videos
        chunk_video_files = []
        for i, chunk in enumerate(chunks):
            chunk_output = os.path.join(temp_dir, f"chunk_{i}.mp4")
            if len(chunk) == 1:
                # Just copy the single video
                shutil.copy(chunk[0], chunk_output)
            else:
                # Concatenate multiple videos
                concatenate_videos(chunk, chunk_output)

            chunk_video_files.append(chunk_output)
            print(f"Chunk {i}: {chunk_durations[i]:.2f} seconds, {len(chunk)} videos")

        # Create the 3x3 montage
        create_3x3_montage(chunk_video_files, output_file, border_size)
        print(f"Final montage created: {output_file}")

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Example usage
    process_videos_into_montage(
        base_directory="./drugs_videos", output_file="drugs_montage.mp4", border_size=4
    )
