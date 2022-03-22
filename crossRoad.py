"""
Creating two object which holds the following:
- Main road, outlining the start and end point of the road.
- Local road, outlining the start and end point of the road.
"""

from scipy.spatial import distance

class mainRoad(object):

    def __init__(self,  startN, endN):
        self.startN = startN
        self.endN = endN

class localRoad(object):

    def __init__(self, startL, endL):
        self.startL = startL
        self.endL = endL

