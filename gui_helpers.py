#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 09:02:46 2026

@author: koz
"""
import tkinter as tk
from tkinter import filedialog, messagebox


def select_video_file():
    """Open a file dialog to select a video file."""
    root = tk.Tk()
    root.withdraw()

    filename = filedialog.askopenfilename(
        title="Select video file",
        filetypes=[
            ("Video files", "*.mp4 *.avi *.mov"),
            ("All files", "*.*")
        ]
    )
    root.destroy()
    return filename


def ask_save_plots():
    """Ask user whether to save generated plots."""
    root = tk.Tk()
    root.withdraw()

    answer = messagebox.askyesno(
        "Save plots",
        "Would you like to save the plots?"
    )
    root.destroy()
    return answer


def ask_save_path(default_name="plot.png"):
    """Ask user where to save a figure."""
    root = tk.Tk()
    root.withdraw()

    path = filedialog.asksaveasfilename(
        title="Save plot",
        defaultextension=".png",
        initialfile=default_name,
        filetypes=[
            ("PNG image", "*.png"),
            ("PDF document", "*.pdf")
        ]
    )
    root.destroy()
    return path
