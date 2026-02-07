#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 09:05:21 2026

@author: koz
"""
import os
import ProcessVideo as ProcessVideo

from gui_helpers import (
    select_video_file,
    ask_save_plots,
    ask_save_path,
)

def get_filename_parts(filename):
    basename = os.path.split(filename)[-1]# Get rid of all the path info except for
    # the file name part. 
    label = os.path.splitext(basename)[0]
    return basename,label

def main():
    data = {}
    # 1. Select file
    video_path = select_video_file()
    if not video_path:
        print("No file selected. Exiting.")
        return
    video_processor = ProcessVideo.BallTracker(pixelscale = (5.91*0.0254)/58.0)
    basename,label = get_filename_parts(video_path)
    data[label] = video_processor.track_yellow_ball(video_path,
                                                 label= label)
    # Data comes back as a list with the following stucture:
    # output_data.append([index,dx,dy,dt,vx,vy,vabs,angle,x_mid,t_mid,tx,ty,times])
    
    # data[index][0] = object id (only one element)
    # data[index][1] = dx values
    # data[index][2] = dy values
    # data[index][3] = dt values
    # data[index][4] = vx.... 
    # x_mid is the midpoint between two x values for a dx, use for plotting with
    # dx, dy, vx, vy, vabs, angle. 
    # t_mid is midpoint in time between two values. Use for plotting with dx
    # dy, vx, or vy, vabs, angle. 
    # tx, ty, and times are the locations of the object in each of the frames. 
    
    write_excel(basename,label,data[label])
    
    return data


def write_excel(basename,label,data):
    import pandas as pd
    
    with pd.ExcelWriter("tracks.xlsx") as writer:
        for track_data in data:
            track_id = track_data[0]
            
            df = pd.DataFrame()
            df['x_mid'] = track_data[8]
            df['t_mid'] = track_data[9]
            df['dx'] = track_data[1]
            df['dy'] = track_data[2]
            df['dt'] = track_data[3]
            df['vx'] = track_data[4]
            df['vy'] = track_data[5]
            df['vabs'] = track_data[6]
            df['angle'] = track_data[7]
            df['x'] = track_data[10][1:]
            df['y'] = track_data[11][1:]
            df['time'] = track_data[12][1:]

            df.to_excel(
                writer,
                sheet_name=f"track_{track_id}",
                index=False
            )

if __name__ == "__main__":
    data = main()
