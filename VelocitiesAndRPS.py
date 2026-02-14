#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 23:41:30 2026

@author: koz
"""
import matplotlib.pyplot as plt
import numpy as np
# Assumes IMG_4490 lines up with 2855s in the log. 
# Naw, that was wrong.  4490 lines up with 1885s.
# need to redo. 
v = np.array([
    [8.25,68.8],
    [8.8,69.0],
    [8.7,69.3],
    [9.3,71.9],
    [8.9,70.1],
    [9.1,71.3],
    [8.6,69.1],
    [9.1,72.0],
    [9.1,69.9],
    [8.5,70.0],
    ])

v2 = np.array([
    [10.96,70.1],
    [11.01,68.9],
    [11.18,71.1],
    [10.43,69.9],
    [11.1,74.0],
    [10.8,68.2],
    [10.56,69.53],
    [11.36,72.65],
    [10.96,70.7],
    [11.1,72.3],
    ])

# 4487 Track 1, 40 rps
v3 = np.array([[7.1,57],])

# 4487 track 2, 45 rps
v4 = np.array([[8.15,55.5],])

rps = np.array([33.36,32.8,31.8,30.57,32.61,33.7,33.3,35.2,31.6,28.9])
rps2 = np.array([37.6,40.65,36.9,34.66, 38.1,36.9,36.95,34.3,38.6,40.9,])
rps3 = np.array([24.6,])
# 4487, 592.9 seconds, 45 rps target
rps4 = np.array([28.7,])
# These are for 2855 and the one after
#rps = np.array([35.9,30.8,30.3,33.1,32.4,29.3,33.9,33.2,31.2,31.1,])
#rps2 = np.array([37.1,40.3,42.1,42.1,38.3,38.7,35.2,39.0,42.0,38.2,])
plt.scatter(42-rps3,v3[:,0],label='40 rps')
plt.scatter(46-rps4,v4[:,0],label='45 rps')
plt.scatter(52.5-rps,v[:,0],label='50 rps')
plt.scatter(61.5-rps2,v2[:,0],label='60 rps')

plt.legend()
plt.grid(True)
plt.xlabel('Delta rps')
plt.ylabel('Velocity m/s')

plt.figure(2)
plt.scatter(42-rps3,v3[:,1],label='40 rps')
plt.scatter(46-rps4,v4[:,1],label='45 rps')
plt.scatter(52.5-rps,v[:,1],label='50 rps')
plt.scatter(61.5-rps2,v2[:,1],label='60 rps')
plt.legend()
plt.grid(True)
plt.xlabel('Delta rps')
plt.ylabel('Angle deg')

plt.figure(3)
plt.scatter(v3[:,0],v3[:,1],label='40 rps')
plt.scatter(v4[:,0],v4[:,1],label='45 rps')
plt.scatter(v[:,0],v[:,1],label='50 rps')
plt.scatter(v2[:,0],v2[:,1],label='60 rps')
plt.legend()
plt.grid(True)
plt.xlabel('Velocity (m/s)')
plt.ylabel('Angle (deg)')