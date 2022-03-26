import random
import simpy
"""
Setting up the environment of which the simulation will run.
"""
RANDOM_SEED = 42
NUM_MAIN = 10 # Number of cars on the main road.
NUM_LOCAL = 5 # Number of cars on the local road.
PASS = 0.1 # Amount of seconds it takes to pass the intersection whilst driving.
CROSS = 0.2 # Amount of seconds it takes to cross the intersection from stopping position.
T_INTER = 3 # Create a car every 7 minutes.
SIM_TIME = 5 # Simulation time in minutes.

class CrossRoad(object):
    """ A cross road consists of two roads, main and local.
    The main road has priority whilst the local road cuts through the main."""
    def __init__(self, env, north, east, num_main, num_local, passtime, crosstime):
        self.env = env
        self.north = north
        self.east = east
        self.num_main = simpy.Resource(env, num_main)
        self.num_local = simpy.Resource(env, num_local)
        self.passtime = passtime
        self.crosstime = crosstime


    def passing(self, carM):
        """ The driving process of a car on the main road past the cross road."""
        yield self.env.timeout(PASS)
        print("Main car passed at %.2f." % self.env.now)

    def crossing(self, carL):
        """ The driving process of a car of the local road to cross the cross road."""
        yield self.env.timeout(CROSS)
        print("Local car crossed at %.2f." % self.env.now)

def carM(env, name, cr):
    """ The car process for the main road, each car has a name (being a number) passes the crossroad (cr)"""
    print("%s approaches the cross road from the main road at %.2f." % (name, env.now))
    with cr.num_main.request() as request:
        yield request

        print("%s drives past the crossroad from the main road at at %.2f." % (name, env.now))
        yield env.process(cr.passing(name))

        print('%s drove past the crossroad from the main road at %.2f.' % (name, env.now))

def carL(env, name, cr):
    """ The car process for the main road, each car has a name (being a number) passes the crossroad (cr)"""
    print("%s approaches the cross road from the local road at %.2f." % (name, env.now))
    with cr.num_local.request() as request:
        yield request

        print("%s drives past the crossroad from the local road at at %.2f." % (name, env.now))
        yield env.process(cr.crossing(name))

        print('%s drove past the crossroad from the local road at %.2f.' % (name, env.now))

def setup(env,num_main, num_local, passtime, crosstime, t_inter):
    """ Create the crossroad with a number of initial cars and keep adding car to the crossroad every minute. """
    # Create the crossroad.
    global i
    crossroad = CrossRoad(env, None, None, num_main, num_local, passtime, crosstime)

    # Create cars on the local road looking to cross.
    for i in range(5):
        env.process(carM(env, 'Car %d' % i, crossroad))

    # Create 2 initial cars on the local road looking to cross.
    for i in range(5):
        env.process(carL(env, 'Car %d' % i, crossroad))

    # Create more cars while the simulation is working.
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1
        env.process(carM(env, 'Car %d' % i, crossroad))
        env.process(carL(env, 'Car %d' % i, crossroad))

# Setup and start the simulation
print("Crossroad:")
random.seed(RANDOM_SEED) # Helps reproduce the results.

# Create an environment and start the setup process.
env = simpy.Environment()
env.process(setup(env, NUM_MAIN, NUM_LOCAL, PASS, CROSS, T_INTER))

# Execute!
env.run(until=SIM_TIME)




