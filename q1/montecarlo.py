"""
Since the pdf function is symettric we can conclude the probibilty that X < Y is half.
Running the simulation we can verify our reasoning.
"""


import sys 
import math
from random import randrange

MAXSIZE = sys.maxsize

def usage():
    return """Usage: montecarlo.py <NumberOfSimulationPoints>"""

def pdf(point):
    x, y = point
    return math.exp(-(x+y))

def prob(predicate, pdf_function, simulation_length):
    random_vector = ((randrange(0, MAXSIZE), randrange(0, MAXSIZE))
                     for _ in range(simulation_length))
    count = len(list(map(pdf, filter(predicate, random_vector))))
    return count/simulation_length

def main(simulation_length):
    constraint = lambda point: point[0] > point[1]
    return prob(constraint, pdf, simulation_length)

if __name__ == '__main__':
    try:
        arg_count = len(sys.argv)
        print(arg_count)
        if arg_count == 2:
            simulation_length = int(sys.argv[1])
        elif arg_count > 2:
            raise Exception(f"Wrong number of arguments {sys.argv}")
    except Exception as e:
        print(e, file=sys.stderr)
        print(usage())
    probability = main(simulation_length)
    print(f"Points={simulation_length} Probability={probability}")
