#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 09:46:10 2026

@author: koz
"""
import numpy as np
from scipy.spatial.distance import cdist


class Track:
    def __init__(self, track_id, centroid):
        self.id = track_id
        self.centroid = np.array(centroid, dtype=float)
        self.velocity = np.zeros(2, dtype=float)
        self.age = 1
        self.missed = 0

    def predict(self):
        return self.centroid + self.velocity


class MultiObjectTracker:
    def __init__(
        self,
        max_distance=30,
        max_missed=5,
    ):
        """
        Parameters
        ----------
        max_distance : float
            Maximum distance for detection ↔ track association (pixels)
        max_missed : int
            Number of consecutive missed frames before a track is deleted
        """
        self.max_distance = max_distance
        self.max_missed = max_missed

        self.tracks = []
        self.next_id = 0

    def update(self, detections):
        """
        Update tracker with detections from the current frame.

        Parameters
        ----------
        detections : list of (y, x) or (row, col)
            Detected object centroids

        Returns
        -------
        tracks : list of Track
            Active tracks after update
        """
        detections = [np.array(d, dtype=float) for d in detections]

        # Case 1: no existing tracks → spawn all
        if len(self.tracks) == 0:
            for d in detections:
                self._start_track(d)
            return self.tracks

        # Case 2: tracks exist but no detections
        if len(detections) == 0:
            for t in self.tracks:
                t.missed += 1
            self._prune_tracks()
            return self.tracks

        # Predict track positions
        predicted = np.array([t.predict() for t in self.tracks])
        dets = np.array(detections)

        # Compute cost matrix (Euclidean distance)
        D = cdist(predicted, dets)

        matched_tracks = set()
        matched_dets = set()

        # Greedy assignment (fast, usually sufficient)
        while True:
            i, j = np.unravel_index(np.argmin(D), D.shape)
            if D[i, j] > self.max_distance:
                break

            self._update_track(self.tracks[i], dets[j])

            matched_tracks.add(i)
            matched_dets.add(j)

            D[i, :] = np.inf
            D[:, j] = np.inf

        # Handle unmatched tracks
        for i, t in enumerate(self.tracks):
            if i not in matched_tracks:
                t.missed += 1

        # Spawn new tracks for unmatched detections
        for j, d in enumerate(dets):
            if j not in matched_dets:
                self._start_track(d)

        self._prune_tracks()
        return self.tracks

    def _start_track(self, detection):
        self.tracks.append(Track(self.next_id, detection))
        self.next_id += 1

    def _update_track(self, track, detection):
        new_pos = detection
        track.velocity = new_pos - track.centroid
        track.centroid = new_pos
        track.age += 1
        track.missed
        
    def _prune_tracks(self):
        self.tracks = [
            t for t in self.tracks if t.missed <= self.max_missed
        ]