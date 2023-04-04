"""This module submits command argument to ffmpeg."""
import subprocess


def submit_ffmpeg(ffmpeg_command):
    """Submits a command constructed in gui module to ffmpeg."""

    p = subprocess.Popen(
        ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode(), stderr.decode()
