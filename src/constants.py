"""Constants"""
FFMPEG_SERVER_PATH = r"//5d-server/PLUGINS/ffmpeg/bin/ffmpeg.exe"
FFMPEG_LOCAL_PATH = r"C:/ffmpeg/bin/ffmpeg.exe"

GUI_WIDTH = 750
GUI_HEIGHT = 600
ENTRY_WIDTH = 540
OPT_WIDTH = 100
SLIDER_WIDTH = 100
CORNER_RADIUS = 30
BTN_RADIUS = 30
TEXTBOX_WIDTH = 800-90
TEXTBOX_HEIGHT = 300

CRF_MIN_VAL = 16
CRF_MAX_VAL = 28
CRF_STEPS = CRF_MAX_VAL - CRF_MIN_VAL
CRF_INIT_VAL = 23

FPS_VALUES = ['2', '4', '8', '15', '24', '30', '48', '60', '120']
H264_PRESET_VALUES = ['ultrafast', 'superfast', 'veryfast', 'faster',
                      'fast', 'medium', 'slow', 'slower', 'veryslow']

ENCODERS = ['libx264', 'libx265']

LIBX264_CONTAINERS = ['mp4', 'mov', 'mkv']
LIBX265_CONTAINERS = ['hevc', 'mp4', 'mov', 'mkv']

FILL_METHODS = ['Repeat', 'Color', 'Black', 'None']

FRAME_PATTERN = r"\.\d{1,10}"
