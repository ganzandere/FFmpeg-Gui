"""Module defining GUI"""
import os
import tempfile
from tkinter import filedialog as fd

import customtkinter as ctk

import constants as c
from utils import (find_ffmpeg, sequence_collector, sequence_step_calc,
                   sequence_writer, submit_ffmpeg)


class App(ctk.CTk):
    """Defines a GUI class."""

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        icon_path = os.path.normpath(f"{os.path.dirname(__file__)}/../icons/ffmpeg.ico")
        self.iconbitmap(icon_path)
        self.title("DK FFmpeg GUI")
        self.geometry(f"{c.GUI_WIDTH}x{c.GUI_HEIGHT}")
        self.maxsize(c.GUI_WIDTH, c.GUI_HEIGHT)
        self.minsize(c.GUI_WIDTH, c.GUI_HEIGHT)

        self.font = ctk.CTkFont("Segoe UI", 12, 'bold')
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # ffmpeg_path
        self.ffmpeg_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.ffmpeg_path_frame.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.ffmpeg_path_entry = ctk.CTkEntry(master=self.ffmpeg_path_frame, placeholder_text="Path to ffmpeg.exe", corner_radius=c.CORNER_RADIUS, font=self.font, width=c.ENTRY_WIDTH)
        self.ffmpeg_path_entry.insert(0, find_ffmpeg())
        self.ffmpeg_path_entry.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        self.ffmpeg_path_browse = ctk.CTkButton(master=self.ffmpeg_path_frame, text='Browse', command=self.ffmpeg_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
        self.ffmpeg_path_browse.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
        # input_path
        self.in_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.in_path_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.input_entry = ctk.CTkEntry(master=self.in_path_frame, placeholder_text="Path to image sequence: ", corner_radius=c.CORNER_RADIUS, font=self.font, width=c.ENTRY_WIDTH)
        self.input_entry.grid(row=0, column=0, padx=10, pady=5)
        self.in_path_browse = ctk.CTkButton(master=self.in_path_frame, text='Browse', command=self.input_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
        self.in_path_browse.grid(row=0, column=1, padx=10, pady=5)
        # container_frame
        self.advanced_frame = ctk.CTkFrame(master=self, bg_color="transparent", fg_color="transparent")
        self.advanced_frame.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        # framerate
        self.fps_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.fps_frame.grid(row=0, column=0, padx=5)
        self.fps_val = ctk.StringVar(value="60")
        self.fps_opt = ctk.CTkOptionMenu(master=self.fps_frame, font=self.font, variable=self.fps_val, values=c.FPS_VALUES,  width=c.OPT_WIDTH-30)
        self.fps_opt.grid(row=0, column=0, padx=10, pady=5)
        self.fps_label = ctk.CTkLabel(master=self.fps_frame, text="Fps", font=self.font)
        self.fps_label.grid(row=0, column=1, padx=10, pady=5)
        # codecs
        self.codec_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.codec_frame.grid(row=0, column=1, padx=5, sticky='nsew')
        self.codec_val = ctk.StringVar(value="libx264")
        self.codec_opt = ctk.CTkOptionMenu(master=self.codec_frame, font=self.font, variable=self.codec_val, values=c.ENCODERS, width=c.OPT_WIDTH, command=self.codec_opt_callback)
        self.codec_opt.grid(row=0, column=0, padx=10, pady=5)
        self.codec_label = ctk.CTkLabel(master=self.codec_frame, text='Codec', font=self.font)
        self.codec_label.grid(row=0, column=1, padx=10, pady=5)
        # presets
        self.preset_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.preset_frame.grid(row=0, column=2, padx=5, sticky='nsew')
        self.preset_val = ctk.StringVar(value="medium")
        self.preset_opt = ctk.CTkOptionMenu(master=self.preset_frame, font=self.font, variable=self.preset_val, values=c.H264_PRESET_VALUES, width=c.OPT_WIDTH)
        self.preset_opt.grid(row=0, column=0, padx=10, pady=5)
        self.preset_label = ctk.CTkLabel(master=self.preset_frame, text="Preset ", font=self.font)
        self.preset_label.grid(row=0, column=1, padx=10, pady=5)
        # CRF
        self.crf_frame = ctk.CTkFrame(master=self.advanced_frame)
        self.crf_frame.grid(row=0, column=3, padx=5, sticky='nsew')
        self.crf_val = ctk.IntVar(value=c.CRF_INIT_VAL)
        self.crf_slider = ctk.CTkSlider(master=self.crf_frame, from_=c.CRF_MIN_VAL,
                                        to=c.CRF_MAX_VAL, variable=self.crf_val, number_of_steps=c.CRF_STEPS, width=c.SLIDER_WIDTH)
        self.crf_slider.grid(row=0, column=0, padx=10, pady=5)
        self.crf_label = ctk.CTkLabel(master=self.crf_frame, text="CRF", font=self.font)
        self.crf_label.grid(row=0, column=1, padx=10, pady=5)
        self.crf_val_label = ctk.CTkLabel(master=self.crf_frame, textvariable=self.crf_val, font=self.font)
        self.crf_val_label.grid(row=0, column=2, padx=10, pady=5)
        # Output filename
        self.out_path_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.out_path_frame.grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.output_entry = ctk.CTkEntry(master=self.out_path_frame, font=self.font,
                                         placeholder_text="Output filename: ", corner_radius=c.CORNER_RADIUS, width=c.ENTRY_WIDTH)
        self.output_entry.grid(row=0, column=0, padx=10, pady=5)
        self.out_path_button = ctk.CTkButton(master=self.out_path_frame, text='Browse',
                                             command=self.output_browse_callback, corner_radius=c.BTN_RADIUS, font=self.font)
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
        self.containers_opt = ctk.CTkOptionMenu(master=self.run_subframe1, values=c.LIBX264_CONTAINERS, variable=self.containers_val, width=c.OPT_WIDTH, font=self.font)
        self.containers_label = ctk.CTkLabel(master=self.run_subframe1, text='Container ', font=self.font)
        self.containers_opt.grid(row=0, column=0, padx=10, pady=5)
        self.containers_label.grid(row=0, column=1, padx=10, pady=5)
        # Fill Method
        self.fill_frame = ctk.CTkFrame(master=self.run_frame)
        self.fill_frame.grid(row=0, column=1, padx=5)
        self.fill_method_val = ctk.StringVar(value='Color')
        self.fill_methods = ctk.CTkOptionMenu(master=self.fill_frame, values=c.FILL_METHODS, variable=self.fill_method_val, width=c.OPT_WIDTH, font=self.font)
        self.fill_methods.grid(row=0, column=0, padx=5, pady=5)
        self.fill_label = ctk.CTkLabel(master=self.fill_frame, text='Fill Method', font=self.font)
        self.fill_label.grid(row=0, column=1, padx=5, pady=5)
        # Run Subframe2
        self.run_subframe2 = ctk.CTkFrame(master=self.run_frame)
        self.run_subframe2.grid(row=0, column=2, padx=5)
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

    def input_browse_callback(self):
        """Defines the behaviour of input path browse button."""
        folder = fd.askopenfilename()
        if folder != "":
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, folder)

    def codec_opt_callback(self, val):
        """Not the best implementation of swapping container lists depending on the codec selected"""
        if val == 'libx264':
            self.containers_opt.configure(values=c.LIBX264_CONTAINERS)
            self.containers_val.set(c.LIBX264_CONTAINERS[0])
        if val == "libx265":
            self.containers_opt.configure(values=c.LIBX265_CONTAINERS)
            self.containers_val.set(c.LIBX265_CONTAINERS[0])

    def output_browse_callback(self):
        """Defines the behaviour of output path browse button."""
        folder = fd.asksaveasfilename(filetypes=((f"{self.containers_opt.get()}", f"*.{self.containers_opt.get()}"), ("All Files", "*.*")))
        self.output_entry.delete(0, "end")
        self.output_entry.insert(0, folder)

    def preview_callback(self):
        """Constructs a preview of command in Log"""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = self.construct_command(temp_dir)
            #Log output
            self.log_textbox.delete("0.0", "end")
            self.log_textbox.insert("0.0", f"\nConstructed ffmpeg command: \n{command}\n")
        
    def run_callback(self):
        """Sends constructed command to ffmpeg."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = self.construct_command(temp_dir)
            #Log output
            self.log_textbox.delete("0.0", "end")
            self.log_textbox.insert("0.0", f"\nConstructed ffmpeg command: \n{command}\n\n")
            stdout, stderr = submit_ffmpeg(command)
            self.log_textbox.insert("end", f"FFmpeg output: {stderr}")

    def construct_command(self, directory):
        """Constructs a ffmpeg command from gui values entered by user."""
        ffmpeg_path = os.path.normpath(self.ffmpeg_path_entry.get())
        input_entry = self.input_entry.get()
        output_stem = os.path.splitext(self.output_entry.get())[0]

        fps = int(self.fps_val.get())
        method = self.fill_method_val.get()
        container = self.containers_val.get()
        output = os.path.normpath(f"{output_stem}.{container}")

        sequence = sequence_collector(input_entry)
        step, missing = sequence_step_calc(sequence)

        if missing:
            if method == 'None':
                missing = []
            else:
                missing = fill(method, directory)

        outfile = sequence_writer(directory, sequence, missing)

        actual_fps = (fps // step)
        # Checks the extension for .exr and sets gamma to 2.2 if True.
        gamma = ""
        if os.path.splitext(sequence[0])[-1] == '.exr':
            gamma = "-gamma 2.2"
        # Logs outfile, step and fps.
        self.log_textbox.delete("0.0", "end")
        self.log_textbox.insert("end", f"List of input frames written to: '{outfile}'.\n")
        self.log_textbox.insert("end", f"\nFrame step detected: {step}.\nEffective input fps is: {actual_fps}\n")
        # Logs missing.
        if missing:
            if missing != "":
                self.log_textbox.insert("end", "\nDetected missing frames:\n")
                for file in missing:
                    self.log_textbox.insert("end", f"{file}\n")
        # Sends command to ffmpeg.
        command = f"{ffmpeg_path} -y {gamma} -r {actual_fps} -f concat -safe 0 -i {outfile} -framerate {self.fps_val.get()} -c:v {self.codec_opt.get()} -crf {self.crf_val.get()} -preset {self.preset_opt.get()} -pix_fmt yuv420p \"{output}\""
        return command
