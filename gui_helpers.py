#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 09:02:46 2026

@author: koz
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np


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

def show_first_frame(frame):
    fig, ax = plt.subplots()
    ax.imshow(frame)
    ax.set_title("Click two points to define scale")
    ax.axis("on")
    return fig, ax


class ScalePicker:
    def __init__(self, image):
        self.image = image
        self.points = []
        self.armed = False

        self.fig, self.ax = plt.subplots()
        self.ax.imshow(image)
        self.ax.set_title(
            "Zoom/pan freely.\n"
            "Press 'x' to start selecting calibration points."
        )
        
        self.done = False
        self.fig.canvas.mpl_connect("close_event", self.on_close)

        self.cid_click = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_click
        )
        self.cid_key = self.fig.canvas.mpl_connect(
            "key_press_event", self.on_key
        )

    def on_key(self, event):
        if event.key == "x":
            
            # Save zoom state
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.armed = True
            self.points.clear()
            self.ax.lines.clear()
            self.ax.set_title(
                "SELECTION MODE:\nClick TWO points, then close window"
            )
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

            self.fig.canvas.draw_idle()
            #self.fig.canvas.draw()

    def on_click(self, event):
        if not self.armed:
            return

        if event.inaxes != self.ax:
            return

        if event.button != 1:
            return

        self.points.append((event.xdata, event.ydata))
        self.ax.plot(event.xdata, event.ydata, "ro")
        self.fig.canvas.draw()

        if len(self.points) == 2:
            self.draw_line()
            self.armed = False
            self.ax.set_title("Points selected — close window")
            self.fig.canvas.draw()

    def draw_line(self):
        (x1, y1), (x2, y2) = self.points
        self.ax.plot([x1, x2], [y1, y2], "r-", linewidth=2)

    def get_scale(self, known_distance):
        plt.show(block=False)
    
        while not self.done:
            plt.pause(0.05)
    
        if len(self.points) != 2:
            raise RuntimeError("Two points not selected")
    
        p1, p2 = np.array(self.points)
        pixel_dist = np.linalg.norm(p2 - p1)
    
        return known_distance / pixel_dist

    
    def on_close(self, event):
        self.done = True


def get_scale_from_user(frame, known_distance_m):
    """
    Parameters
    ----------
    frame : ndarray
        Image array (H x W x 3)
    known_distance_m : float
        Real-world distance between the two clicked points (meters)

    Returns
    -------
    meters_per_pixel : float
    """
    fig, ax = show_first_frame(frame)

    print("Please click TWO points that are a known distance apart.")
    points = plt.ginput(2, timeout=-1)  # waits until 2 clicks

    if len(points) != 2:
        raise RuntimeError("Exactly two points required")

    (x1, y1), (x2, y2) = points

    pixel_distance = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    meters_per_pixel = known_distance_m / pixel_distance
    
    ax.plot([x1, x2], [y1, y2], "r-o", linewidth=2)
    ax.text(
        (x1+x2)/2, (y1+y2)/2,
        f"{known_distance_m} m",
        color="red",
        fontsize=12)

    return meters_per_pixel
