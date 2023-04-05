"""Helper functions non-related to GUI custom tkinter class"""
import os
import re
import subprocess

import constants as c


def sequence_collector(file_path):
    """Takes a filename and finds it's sequence if there's any."""
    directory, filename = os.path.split(file_path)
    prefix, extension = os.path.splitext(filename)
    prefix = re.sub(r'\.\d{1,10}$', lambda x: c.FRAME_PATTERN, prefix)
    pattern = f"^{prefix}{extension}$"
    files = [os.path.join(directory, f) for f in os.listdir(directory) if re.match(pattern, f)]
    return files


def sequence_step_calc(sequence_list):
    """Takes an image sequence list and returns step between frames as integers."""
    steps = []
    missing = []

    for i in range(len(sequence_list)-1):
        step = frame_extractor(sequence_list[i]) - frame_extractor(sequence_list[i+1])
        steps.append(step)

    if len(set(steps)) > 1:
        step = abs((max(set(steps), key=steps.count)))
        missing = detect_missing_frames(sequence_list, step)

    step = abs(step)
    return step, missing


def detect_missing_frames(sequence_list, step):
    """Determines missing frames in a sequence by n-steps from first to last frame"""
    padding_num = len(re.findall(c.FRAME_PATTERN, sequence_list[0])[-1].replace(".", ""))
    first_frame = int(re.findall(c.FRAME_PATTERN, sequence_list[0])[-1].replace(".", ""))
    last_frame = int(re.findall(c.FRAME_PATTERN, sequence_list[-1])[-1].replace(".", ""))

    missing = []

    for i in range(first_frame, last_frame, step):
        padding = f"{i}".zfill(padding_num)
        search_pattern = re.sub(c.FRAME_PATTERN, f".{padding}", sequence_list[0])
        if search_pattern not in sequence_list:
            missing.append(os.path.normpath(search_pattern))
    return missing


def frame_extractor(file):
    """Takes a frame filename and returns just the frame number as integer."""
    frame = re.findall(c.FRAME_PATTERN, file)[-1].replace(".", "")
    return int(frame)


def sequence_formatter(sequence_list):
    """Takes a sequence list and returns a ffmpeg-formatted input argument."""
    filename = os.path.split(sequence_list[0])
    frame = re.findall(c.FRAME_PATTERN, filename[-1])[-1].replace(".", "")
    formatted_sequence = os.path.join(filename[0], re.sub(c.FRAME_PATTERN, r".%0{}d".format(len(frame)), filename[1]))
    return formatted_sequence


def sequence_writer(directory, sequence_list, missing):
    """Write file sequence to txt.file"""
    merged_list = []
    merged_list = sequence_list + missing
    merged_list.sort()

    with open(f"{directory}/ffmpeg_input.txt", "wb") as outfile:
        for filename in sequence_list:
            outfile.write(f"file '{os.path.normpath(filename)}'\n".encode())
    return os.path.normpath(os.path.join(directory, "ffmpeg_input.txt"))


def find_ffmpeg():
    """Returns ffmpeg.exe path found on system"""
    ffmpeg_path = ""
    if "FFMPEG_PATH" in os.environ:
        if os.path.isfile(os.environ["FFMPEG_PATH"]):
            ffmpeg_path = os.environ["FFMPEG_PATH"]
    elif os.path.isfile(c.FFMPEG_SERVER_PATH):
        ffmpeg_path = c.FFMPEG_SERVER_PATH
    elif os.path.isfile(c.FFMPEG_LOCAL_PATH):
        ffmpeg_path = c.FFMPEG_LOCAL_PATH
    return ffmpeg_path


def submit_ffmpeg(ffmpeg_command):
    """Submits a command constructed in gui module to ffmpeg."""

    p = subprocess.Popen(
        ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode(), stderr.decode()
