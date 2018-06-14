import pymel.core as pmc
import logging

class BakeRange(object):

    def __init__(self, time_range=None, callback=None):

        if not time_range:
            time_range = (pmc.playbackOptions(minTime=True, q=True), pmc.playbackOptions(maxTime=True, q=True))

        for frame in range(int(time_range[1] - time_range[0])):
            print frame
            callback(frame + time_range[0])
