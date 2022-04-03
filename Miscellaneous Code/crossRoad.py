from collections import deque # double-ended queue
from numpy import random
import simpy
from simpy.util import start_delayed
"""
Setting up the environment of which the simulation will run.
"""

class CrossRoad(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Initialisation
random.seed([1, 2, 3])

# Simulation time in seconds.
SIM_TIME = 3.0

# Cars on the main road arrive at the crossroad according to a Poisson process with an average rate of 0.8 per second:
Main_arrival_rate= 0.8
Main_t_interarrival_mean= 1.0 / Main_arrival_rate

# Cars on the local road arrive at the crossroad according to a Poisson process with an average rate of 0.5 per second:
Local_arrival_rate= 0.8
Local_t_interarrival_mean= 1.0 / Local_arrival_rate

# Duration to pass or cross the cross road.
#t_PASS = 0.3; t_CROSS = 0.7

# The time for a car at the head of the queue on the local road to depart (clear the intersection)
# is modeled as a triangular distribution with specified minimum, maximum, and
# mode.
t_depart_left= 1.6; t_depart_mode= 2.0; t_depart_right= 2.4

# Initially, no cars are waiting at the crossroad incoming from the local road:
queue= deque()

# Track number of cars on the main road:
main_arrival_count= main_departure_count= 0

# Track number of cars on the local road:
local_arrival_count= local_departure_count= 0

Q_stats= CrossRoad(count=0, cars_waiting=0)
W_stats= CrossRoad(count=0, waiting_time=0.0)

# NUM_MAIN = 10 # Number of cars on the main road.
# NUM_LOCAL = 5 # Number of cars on the local road.
#
# T_INTER = 3 # Create a car every 7 minutes.


mainCar = {}
name = ""


""" A cross road consists of two roads, main and local.
    # The main road has priority whilst the local road cuts through the main."""
    # def __init__(self, env, num_main, num_local, passtime, crosstime):
    #     self.env = env
    #     self.num_main = simpy.Resource(env, num_main)
    #     self.num_local = simpy.Resource(env, num_local)
    #     self.passtime = passtime
    #     self.crosstime = crosstime


    # def passing(self, carM):
    #     """ The driving process of a car on the main road past the cross road."""
    #     yield self.env.timeout(PASS)
    #     print("Main car passed at %.2f." % self.env.now)
    #
    # def crossing(self, carL):
    #     """ The driving process of a car of the local road to cross the cross road."""
    #     yield self.env.timeout(CROSS)
    #     print("Local car crossed at %.2f." % self.env.now)

def carM():

    global mainCar, main_arrival_count, env, name, queue
    name = main_arrival_count
    mainCar = {"name": name, "time": env.now}
    crossroad = CrossRoad()
    direction = random.randint(1, 2)

    if direction == 1:
        direction = "North"
    else:
        direction = "South"

    """ The car process for the main road, each car has a name (being a number) passing the crossroad (cr)"""
    print("Main road car #%s approaches the crossroad from the %s direction at %.2f." % (name, direction, env.now))

    # for i in range(4):
    #     env.process(carM())

    while True:
        main_arrival_count += 1
    # with cr.num_main.request() as request:
    #     yield request
    #
    #     print("%s drives past the crossroad from the main road at at %.2f." % (name, env.now))
    #     yield env.process(cr.passing(name))

        # Schedule next arrival:
        yield env.timeout(random.exponential(Main_t_interarrival_mean))


def carL_arrival(): # Defining the arrival of a local car to the cross road.
    """ The car process for the local road, each car has a name (being a number) looking to cross the crossroad (cr)"""
    global local_arrival_count, env, name, mainCar, queue
    name = local_arrival_count

    direction = random.randint(1, 2)

    if direction == 1:
        direction = "East"
    else:
        direction = "West"
    print("Local rod car #%s approaches the cross road from %s direction at time %.2f." % (name, direction, env.now))

    while True:
        local_arrival_count += 1

        if(mainCar.get("time") == env.now) or len(queue):
        # There are cars on the main road and the cars on the local road cannot pass.
        # They join the queue to cross the crossroad.
            queue.append((local_arrival_count, env.now))
            print("Car #%d arrived and joined the queue at this position %d at time " "%.3f" % (local_arrival_count, len(queue), env.now))

        # print("%s drives past the crossroad from the local road at at %.2f." % (name, env.now))
        # yield env.process(cr.crossing(name))

        else:
            print("Local road car #%d arrived to no cars at the crossroad at time " " %.3f." % (local_arrival_count, env.now))

        # Record waiting time statistics.  (This car experienced zero waiting
        # time, so we increment the count of cars, but the cumulative waiting
        # time remains unchanged.
            W_stats.count += 1

    # Schedule next arrival:
        yield env.timeout(random.exponential(Local_t_interarrival_mean))

# Declaring the departure of the local car from the cross road.
def carL_departure():
    """
       This generator function simulates the 'departure' of a car, i.e., a car that
       previously entered the intersection clears the intersection.  Once a car has
       departed, we remove it from the queue, and we no longer track it in the
       simulation.
       """
    global env, queue

    while True:
        car_number, t_arrival = queue.popleft()
        print("Local road car #%d departed at time %.3f, leaving %d cars in the queue." % (car_number, env.now, len(queue)))

        W_stats.count += 1
        W_stats.waiting_time += env.now - t_arrival

    # If the crossroad is busy or the local road queue is empty, do not schedule the next departure.
        if(mainCar.get("time") == env.now) or len(queue) == 0:
            return

    # Produce the departure delay as a random draw from the triangular distribution:
        delay = random.triangular(left=t_depart_left, mode=t_depart_mode, right=t_depart_right)

    # Schedule the next departure:
        yield env.timeout(delay)

def monitor():
   """
   This generator function produces an interator that collects statistics on the
   state of the queue at regular intervals.  An alternative approach would be to
   apply the PASTA property of the Poisson process ('Poisson Arrivals See Time
   Averages') and sample the queue at instants immediately prior to arrivals.
   """
   global env, Q_stats

   while True:
        Q_stats.count+= 1
        Q_stats.cars_waiting+= len(queue)
        yield env.timeout(1.0)


# Section 5: Schedule initial events and run the simulation.  Note: The first
# change of the traffic light, first arrival of a car, and first statistical
# monitoring event are scheduled by invoking `env.process`.  Subsequent changes
# will be scheduled by invoking the `timeout` method.  With this scheme, there
# is only one event of each of these types scheduled at any time; this keeps the
# event queue short, which is good for both memory utilization and running time.

print("\nSimulation of Cars Arriving at Intersection without Traffic Lights "
  "Light\n\n")

# Initialize environment:
env= simpy.Environment()

# Schedule first change of the traffic light:
#env.process(light())

# Schedule first arrival of a car on the main road:
Main_t_first_arrival= random.exponential(Main_t_interarrival_mean)
start_delayed(env, carM(), delay=Main_t_first_arrival)

# Schedule first arrival of a car on the local road:
Local_t_first_arrival= random.exponential(Local_t_interarrival_mean)
start_delayed(env, carL_arrival(), delay=Local_t_first_arrival)

# Schedule first statistical monitoring event:
env.process(monitor())

# Let the simulation run for specified time:
env.run(until=SIM_TIME)


# Section 6: Report statistics.

print("\n\n      *** Statistics ***\n\n")

print("Mean number of cars waiting: %.3f" % (Q_stats.cars_waiting / float(Q_stats.count)))

print("Mean waiting time (seconds): %.3f" % (W_stats.waiting_time / float(W_stats.count)))



# def setup(env,num_main, num_local, passtime, crosstime, t_inter):
#     """ Create the crossroad with a number of initial cars and keep adding car to the crossroad every minute. """
#     # Create the crossroad.
#     global i
#     crossroad = CrossRoad(env, None, None, num_main, num_local, passtime, crosstime)
#
#     # Create cars on the local road looking to cross.
#     for i in range(1):
#         env.process(carM(env, 'Car %d' % i, crossroad))
#
#     # Create 2 initial cars on the local road looking to cross.
#     for i in range(1):
#         env.process(carL(env, 'Car %d' % i, crossroad))
#
#     # Create more cars while the simulation is working.
#     while True:
#         yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
#         i += 1
#         env.process(carM(env, 'Car %d' % i, crossroad))
#         env.process(carL(env, 'Car %d' % i, crossroad))
#
# # Setup and start the simulation
# print("Crossroad:")
# random.seed(RANDOM_SEED) # Helps reproduce the results.
#
# # Create an environment and start the setup process.
# env = simpy.Environment()
# env.process(setup(env, NUM_MAIN, NUM_LOCAL, PASS, CROSS, T_INTER))
#
# # Execute!
# env.run(until=SIM_TIME)




