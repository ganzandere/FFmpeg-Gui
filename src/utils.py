"""Helper functions non-related to GUI custom tkinter class"""
import os
import re
import subprocess

import imageio.v3 as iio

import constants as c


def sequence_collector(file_path):
    """Takes a filename and finds it's sequence if there's any."""
    directory, filename = os.path.split(file_path)
    prefix, extension = os.path.splitext(filename)
    prefix = re.sub(r'\.\d{1,10}$', lambda x: c.FRAME_PATTERN, prefix)
    pattern = f"^{prefix}{extension}$"
    files = [os.path.normpath(os.path.join(directory, f)) for f in os.listdir(directory) if re.match(pattern, f)]
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


def sequence_writer(directory, sequence_list, missing, placeholder_img):
    """Write file sequence to txt.file"""
    merged_list = []
    final_list = []
    merged_list = sequence_list + missing
    merged_list.sort()

    for idx, image in enumerate(merged_list):
        if image in missing:
            if placeholder_img:
                final_list.append(placeholder_img)
            else:
                result = (find_nearest(merged_list, idx))
                if result:
                    final_list.append(result)
        else:
            final_list.append(image)

    with open(f"{directory}/ffmpeg_input.txt", "wb") as outfile:
        for filename in final_list:
            outfile.write(f"file '{os.path.normpath(filename)}'\n".encode())
    return os.path.normpath(os.path.join(directory, "ffmpeg_input.txt"))

def find_nearest(sequence, idx):

    for i in range(idx, 0, -1):
        if os.path.isfile(sequence[i]):
            return sequence[i]
    for i in range(idx + 1, len(sequence)-1):
        if os.path.isfile(sequence[i]):
            return sequence[i]

def dummy_convert(dummy, format, directory):
    """Converts a dummy placeholder image to format matching the sequence thats encoded."""
    if format == ".exr":
        exr_dummy = f"{os.path.splitext(dummy)[0]}{format}"
        return exr_dummy

    im = iio.imread(dummy)
    new_dummy = os.path.join(directory, f"dummy_img{format}")
    diskimage = iio.imwrite(new_dummy, im)
    return(new_dummy)

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
