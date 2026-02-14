#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 19:18:12 2026

@author: koz
"""
import numpy as np
import skimage
import skimage.measure
import cv2
import os
import glob
import matplotlib.pyplot as plt
import av
import MultiobjectTracker

# diameter of the ball was 58 pixels = 5.91 inches
scale = (5.91*0.0254)/58.0 # meters/pixel
class BallTracker():
    
    def __init__(self,pixelscale):
        
        self.gaussian_kernel = 9 # used to blur the image
        # which improves the ball tracking. Creates a loss of 
        # resolution though, so don't go too high.  9-11 is an ok 
        # number in testing, 
        
        # lower_yellow and upper_yellow are the limits for 
        # segmenting based on color.  These worked ok with the initial 
        # testing, might need to be adjusted on a case by case basis. 
        self.lower_yellow = np.array([22, 93, 0], dtype="uint8")
        self.upper_yellow = np.array([45, 255, 255], dtype="uint8")
        
        # These are the properties to keep track of once the image is 
        # segmented.  The segmented image will be processed by
        # the skimage labeler, which finds connected regions.
        # These are the returned properties of those regions. 
        self.properties = ('area','centroid','bbox','eccentricity','equivalent_diameter_area','label')

        self.pixelscale =  pixelscale       
        
        self.tracker = MultiobjectTracker.MultiObjectTracker(max_distance=250) # pixels)

        self.minimum_area = 500 # number of pixels to be considered a ball. 

        return
    
    def convert_video_to_image(self,video_frame):
        # Convert the video frame to an rgb image. 
        img_rgb = video_frame.to_ndarray(format="rgb24")
        
        # Apply a gaussian blur to take smooth the image for easier processing.
        blurred = cv2.GaussianBlur(img_rgb, (self.gaussian_kernel, self.gaussian_kernel), 0)
        
        # Convert the image to HSV, where it is easier to segement the yellow. 
        image = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        return image 


    def segment_image(self,image):
        # This does the segmentation.  It compares the HSV image to the upper 
        # and lower range and only keeps those in the 'yellow' range. 
        mask = cv2.inRange(image, self.lower_yellow, self.upper_yellow)
    
        # Use skimage measure tools to 'label' the image.  This finds connected
        # blobs in the masked image.  The largest yellow blob should be our ball. 
        labels = skimage.measure.label(mask)
        
        # Look up properties for the labeled features
        regions = skimage.measure.regionprops_table(labels,properties=self.properties)
        # Regions are sorted by area, we want the largest yellow blob, at the 0th index. 
        return regions

    def track_yellow_ball(self,filename, label = 'Video'):
        fig,ax = plt.subplots()
        trajectories = {}
        # Read in the video.  This opens the video, but doesn't read all the frames yet. 
        with av.open(filename) as video:
            stream = video.streams.video[0]
        
            # Get the number of frames and then allocate the numpy arrays we'll
            # use to store the data. 
            number_frames = stream.frames
            
            for i, frame in enumerate(video.decode(stream)):
                #print('frame {0}'.format(i))
                # pts * time_base = seconds
                # This gets the time stamp for each frame. 
                timestamp_sec = float(frame.pts * stream.time_base)
                #print('timestamp_sec {0}'.format(timestamp_sec))
                image = self.convert_video_to_image(frame)
                regions = self.segment_image(image)
                valid_detections = regions['area'] > self.minimum_area
                detections = np.column_stack((regions['centroid-0'][valid_detections],regions['centroid-1'][valid_detections]))
                tracks = self.tracker.update(detections)
                for t in tracks:
                    y, x = t.centroid
                    # y needs to be inverted, since y=0 starts at the 
                    # top of the image and works down. 
                    y = image.shape[0]-y 
                    track_id = t.id
                    ax.plot(x*self.pixelscale, y*self.pixelscale, "ro")
                    ax.text((x + 5)*self.pixelscale, (y + 5)*self.pixelscale, str(track_id), color="red")
                    if track_id in trajectories:
                        trajectories[track_id].append([x,y,timestamp_sec])
                    else:
                        trajectories[track_id] = [[x,y,timestamp_sec]]
        
            # All of the frames have been processed for this video.
            # For each of the trajectories, figure out the 
            # velocity vs time at each point. 
            plt.figure('Velocities')
            output_data = []
            for index, trajectory in enumerate(trajectories):
                data = np.array(trajectories[index])
                tx = data[:,0]*self.pixelscale
                ty = data[:,1]*self.pixelscale
                times = data[:,2]
                dx = np.diff(tx)
                dy = np.diff(ty)
                dt = np.diff(times)
                t_mid = (times[:-1]+times[1:])/2
                x_mid = (tx[:-1]+tx[1:])/2
                vx = dx/dt
                vy = dy/dt
                vabs = np.sqrt(vx**2+vy**2)
                angle = np.degrees(np.arctan2(vy,vx))
                plt.plot(x_mid,vabs)
                output_data.append([index,dx,dy,dt,vx,vy,vabs,angle,x_mid,t_mid,tx,ty,times])
                
            
        # x = x*self.pixelscale # make x to be in meters instead of pixels.
        # y = (1000-y)*self.pixelscale # The image coordinates start at the top of the image as
        # # y =0, then increase going to the bottom of the image.  The 1000-y flips the 
        # # y value so increases going up. 
        
        # # Get the change in centroid location between each frame.
        # dx = np.diff(x)
        # dy = np.diff(y)
        
        # plt.figure('Trajectory')
        # plt.scatter(x,y,label=label)    
        # plt.xlabel('Distance (meters)')
        # plt.ylabel('Height (meters)')
        # dt = np.diff(timestamps)
        # plt.grid(True)
        # plt.legend()
        
        # # Velocities.
        # vx = dx/dt
        # vy = dy/dt
        
        # plt.figure('velocities vs time')
        # plt.plot(timestamps[1:],vx,label='vx')
        # plt.plot(timestamps[1:],vy,label='vy')
        # plt.grid(True)
        # plt.xlabel('Time (s)')
        # plt.ylabel('Velocity (m/s)')
        # plt.legend()
        
        # # Compute the total velocity, the root-mean-square of the two velocity components.
        # velocity = np.sqrt(vx**2+vy**2)
        # # Get the angle of the trajectory vs time. 
        # angle = np.degrees(np.arctan2(vy,vx))
        
        # plt.figure('Velocity vs time')
        # plt.plot(timestamps[1:],velocity,label=label)
        # plt.xlabel('time (s)')
        # plt.ylabel('Velocity (m/s)')
        # plt.grid(True)
        # plt.legend()
        
        # plt.figure('Angle vs time')
        # plt.plot(timestamps[1:],angle,label=label)
        # plt.xlabel('time (s)')
        # plt.ylabel('Angle (deg)')
        # plt.grid(True)
        # plt.legend()
        
        # return velocity, angle
        return output_data

# if __name__ == "__main__" :
#     filelist = sorted(glob.glob(directory + '*.mp4'))
    
#     data = {}
    
#     for filename in filelist:
        
#         basename = os.path.split(filename)[-1]# Get rid of all the path info except for
#         # the file name part. 
#         label = os.path.splitext(basename)[0]
#         data[label] = track_yellow_ball(filename, scale, label= label)




