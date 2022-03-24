"""
Setting up the environment of which the simulation will run.
"""
PASS = 0.05 # Amount of seconds it takes to pass the intersection whilst driving.
CROSS = 0.8 # Amount of seconds it takes to cross the intersection from stopping position.
class CrossRoad(object):
    """ A cross road consists of two roads, main and local.
    The main road has priority whilst the local road cuts through the main."""
    def __init__(self, env, north, south, west, east, passtime, crosstime):
        self.env = env
        self.north = north
        self.south = south
        self.west = west
        self.east = east
        self.passtime = passtime
        self.crosstime = crosstime

    def passing(self, car):
        """ The driving process of a car on the main road past the cross road."""
        yield self.env.timeout(PASS)
        print("Main car passed at %d" % self.env.now)

    def crossing(self, car):
        """ The driving process of a car of the local road to cross the cross road."""
        yield self.env.timeout(CROSS)
        print("Local car crossed at %d" % self.env.now)




