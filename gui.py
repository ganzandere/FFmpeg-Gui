"""Module defining GUI"""
import os
from tkinter import filedialog as fd

import customtkinter as ctk

import constants as c
from helpers import (resource_path, sequence_collector, sequence_step_calc, sequence_writer)
from submit import submit_ffmpeg


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # icon_path = resource_path(r'C:\Users\Kristina-PC\Desktop\Sibin\ffmpeg_gui\images\ffmpeg.ico')
        # self.iconbitmap(icon_path)
        self.title("DK FFmpeg GUI")
        self.geometry(f"{c.GUI_WIDTH}x{c.GUI_HEIGHT}")
        self.maxsize(c.GUI_WIDTH, c.GUI_HEIGHT)
        self.minsize(c.GUI_WIDTH, c.GUI_HEIGHT)
        self.get_screen_center()

        self.font = ctk.CTkFont("Inter", 12, "bold")
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # ffmpeg_path
        self.ffmpeg_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.ffmpeg_path_frame.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.ffmpeg_path_entry = ctk.CTkEntry(master=self.ffmpeg_path_frame, placeholder_text="Path to ffmpeg.exe", corner_radius=c.CORNER_RADIUS, font=self.font, width=c.ENTRY_WIDTH)
        self.ffmpeg_path_entry.insert(0, c.FFMPEG_PATH)
        self.ffmpeg_path_entry.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        self.ffmpeg_path_browse = ctk.CTkButton(master=self.ffmpeg_path_frame, text='Browse', command=self.ffmpeg_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
        self.ffmpeg_path_browse.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
        # input_path
        self.in_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.in_path_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.in_path_entry = ctk.CTkEntry(master=self.in_path_frame, placeholder_text="Path to image sequence: ", corner_radius=c.CORNER_RADIUS, font=self.font, width=c.ENTRY_WIDTH)
        self.in_path_entry.grid(row=0, column=0, padx=10, pady=5)
        self.in_path_browse = ctk.CTkButton(master=self.in_path_frame, text='Browse', command=self.in_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
        self.in_path_browse.grid(row=0, column=1, padx=10, pady=5)
        # container_frame
        self.advanced_frame = ctk.CTkFrame(master=self, bg_color="transparent", fg_color="transparent")
        self.advanced_frame.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        # framerate
        self.fps_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.fps_frame.grid(row=0, column=0, padx=5)
        self.fps_val = ctk.StringVar(value="60")
        self.fps_opt = ctk.CTkOptionMenu(master=self.fps_frame, font=self.font, variable=self.fps_val, values=c.FPS_VALUES, width=70)
        self.fps_opt.grid(row=0, column=0, padx=10, pady=5)
        self.fps_label = ctk.CTkLabel(master=self.fps_frame, text="Fps", font=self.font)
        self.fps_label.grid(row=0, column=1, padx=10, pady=5)
        # codecs
        self.codec_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.codec_frame.grid(row=0, column=1, padx=5, sticky='nsew')
        self.codec_val = ctk.StringVar(value="libx264")
        self.codec_opt = ctk.CTkOptionMenu(master=self.codec_frame, font=self.font, variable=self.codec_val, values=c.ENCODERS, width=100, command=self.codec_opt_callback)
        self.codec_opt.grid(row=0, column=0, padx=10, pady=5)
        self.codec_label = ctk.CTkLabel(master=self.codec_frame, text='Codec', font=self.font)
        self.codec_label.grid(row=0, column=1, padx=10, pady=5)
        # presets
        self.preset_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.preset_frame.grid(row=0, column=2, padx=5, sticky='nsew')
        self.preset_val = ctk.StringVar(value="medium")
        self.preset_opt = ctk.CTkOptionMenu(master=self.preset_frame, font=self.font, variable=self.preset_val, values=c.H264_PRESET_VALUES, width=100)
        self.preset_opt.grid(row=0, column=0, padx=10, pady=5)
        self.preset_label = ctk.CTkLabel(master=self.preset_frame, text="Preset ", font=self.font)
        self.preset_label.grid(row=0, column=1, padx=10, pady=5)
        # CRF
        self.crf_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.crf_frame.grid(row=0, column=3, padx=5, sticky='nsew')
        self.crf_val = ctk.IntVar(value=c.CRF_INIT_VAL)
        self.crf_slider = ctk.CTkSlider(master=self.crf_frame, from_=c.CRF_MIN_VAL,
                                        to=c.CRF_MAX_VAL, variable=self.crf_val, number_of_steps=c.CRF_STEPS, width=100)
        self.crf_slider.grid(row=0, column=0, padx=10, pady=5)
        self.crf_label = ctk.CTkLabel(master=self.crf_frame, text="CRF", font=self.font)
        self.crf_label.grid(row=0, column=1, padx=10, pady=5)
        self.crf_val_label = ctk.CTkLabel(master=self.crf_frame, textvariable=self.crf_val, font=self.font)
        self.crf_val_label.grid(row=0, column=2, padx=10, pady=5)
        # Output filename
        self.out_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.out_path_frame.grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.out_path_entry = ctk.CTkEntry(master=self.out_path_frame, font=self.font,
                                           placeholder_text="Output filename: ", corner_radius=c.CORNER_RADIUS, width=c.ENTRY_WIDTH)
        self.out_path_entry.grid(row=0, column=0, padx=10, pady=5)
        self.out_path_button = ctk.CTkButton(master=self.out_path_frame, text='Browse',
                                             command=self.out_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
        self.out_path_button.grid(row=0, column=1, padx=10, pady=5)
        # Log
        self.log_frame = ctk.CTkFrame(master=self)
        self.log_frame.grid(row=8, column=0, padx=10, pady=5)
        self.log_label = ctk.CTkLabel(master=self.log_frame, text="Log", font=self.font)
        self.log_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.log_textbox = ctk.CTkTextbox(master=self.log_frame, font=self.font, width=c.TEXTBOX_WIDTH, height=c.TEXTBOX_HEIGHT, wrap="none")
        self.log_textbox.grid(row=1, column=0, padx=0, pady=0)
        # Run
        self.run_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.run_frame.grid(row=7, column=0, padx=10, pady=5, sticky='w')
        self.run_frame.grid_columnconfigure(0, weight=0)
        self.run_frame.grid_columnconfigure(1, weight=1)
        # Run Subframe1
        self.run_subframe1 = ctk.CTkFrame(master=self.run_frame)
        self.run_subframe1.grid(row=0, column=0, padx=5)
        self.containers_val = ctk.StringVar(value='mp4')
        self.containers_opt = ctk.CTkOptionMenu(master=self.run_subframe1, values=c.LIBX264_CONTAINERS, variable=self.containers_val, width=100, font=self.font)
        self.containers_label = ctk.CTkLabel(master=self.run_subframe1, text='Container ', font=self.font)
        self.containers_opt.grid(row=0, column=0, padx=10, pady=5)
        self.containers_label.grid(row=0, column=1, padx=10, pady=5)
        # Run Subframe2
        self.run_subframe2 = ctk.CTkFrame(master=self.run_frame)
        self.run_subframe2.grid(row=0, column=1, padx=5)
        self.preview_button = ctk.CTkButton(master=self.run_subframe2, text='Preview', font=self.font, command=self.preview_callback)
        self.preview_button.grid(row=0, column=0, padx=10, pady=5)
        self.run_button = ctk.CTkButton(master=self.run_subframe2, text='Run', font=self.font, command=self.run_callback)
        self.run_button.grid(row=0, column=1, padx=10, pady=5)

    def ffmpeg_browse_callback(self):
        """Defines the behaviour of ffmpeg path browse button."""
        folder = fd.askopenfilename()
        if folder != "":
            self.ffmpeg_path_entry.delete(0, "end")
            self.ffmpeg_path_entry.insert(0, folder)

    def in_browse_callback(self):
        """Defines the behaviour of input path browse button."""
        folder = fd.askopenfilename()
        if folder != "":
            self.in_path_entry.delete(0, "end")
            self.in_path_entry.insert(0, folder)

    def codec_opt_callback(self, val):
        """Not the best implementation of swapping container lists depending on the codec selected"""
        if val == 'libx264':
            self.containers_opt.configure(values=c.LIBX264_CONTAINERS)
            self.containers_val.set(c.LIBX264_CONTAINERS[0])
        if val == "libx265":
            self.containers_opt.configure(values=c.LIBX265_CONTAINERS)
            self.containers_val.set(c.LIBX265_CONTAINERS[0])

    def out_browse_callback(self):
        """Defines the behaviour of output path browse button."""
        folder = fd.asksaveasfilename()
        self.out_path_entry.delete(0, "end")
        self.out_path_entry.insert(0, folder)

    def preview_callback(self):
        """Constructs a preview of command in log"""
        command = self.construct_command()
        # self.log_textbox.delete("0.0", "end")
        self.log_textbox.insert("end", f"\nConstructed ffmpeg command: \n{command}\n")

    def run_callback(self):
        """Sends constructed command to ffmpeg."""
        command = self.construct_command()
        self.log_textbox.delete("0.0", "end")
        stdout, stderr = submit_ffmpeg(command)
        self.log_textbox.insert("end", f"FFmpeg output: {stderr}")

    def construct_command(self):
        """Constructs a ffmpeg command from gui values entered by user."""
        output = self.out_path_entry.get()
        output = "{}.{}".format(os.path.splitext(
            output)[0], self.containers_val.get())
        sequence = sequence_collector(self.in_path_entry.get())
        split_path = os.path.split(self.in_path_entry.get())
        outfile = sequence_writer(split_path[0], sequence)
        step, missing = sequence_step_calc(sequence)
        actual_fps = (int(self.fps_val.get()) // step)
        self.log_textbox.delete("0.0", "end")
        self.log_textbox.insert("end", f"List of input frames written to: '{outfile}'.\n")
        self.log_textbox.insert("end", f"\nFrame step detected: {step}.\nEffective input fps adjusted to: {actual_fps}\n")
        if missing != "":
            self.log_textbox.insert("end", "\nDetected missing frames:\n")
            for file in missing:
                self.log_textbox.insert("end", f"{file}\n")
        self.command = f"""{c.FFMPEG_PATH} -y -r {actual_fps} -f concat -safe 0 -i {outfile} -framerate {self.fps_val.get()} -pix_fmt yuv420p -c:v {self.codec_opt.get()} -crf {self.crf_val.get()} -preset {self.preset_opt.get()} {output}"""

        return self.command

    def get_screen_center(self):
        """Should position a new window to the screen center but doesn't."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_rootx() - self.winfo_width()) // 2
        y = (screen_height - self.winfo_rooty() - self.winfo_height()) // 2
        self.geometry("+{}+{}".format(x, y))
