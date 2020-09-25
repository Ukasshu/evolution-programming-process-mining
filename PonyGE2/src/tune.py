#! /usr/bin/env python

# PonyGE2
# Copyright (c) 2017 Michael Fenton, James McDermott,
#                    David Fagan, Stefan Forstenlechner,
#                    and Erik Hemberg
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from timeit import default_timer as timer
from stats.stats import __get_stats__
from algorithm.parameters import params, set_params
import sys
import re

def tune():
    """ Run program """

    # Run evolution
    individuals = params['SEARCH_LOOP']()

    stats = __get_stats__(individuals, end = True)

    return stats["ave_fitness"], stats["gen"]

def print_results(seed, fitness, duration, length):
    print("Result for SMAC: SAT,{},{},{},{},0".format(duration, length, 100 - fitness, seed))

def preprocess_parameters(cmd_line_params):
    def add_dash(name):
        return "-{}".format(name)
    keys = cmd_line_params[::2]
    values = cmd_line_params[1::2]
    cmd_line_params_dict = dict(zip(keys, values))
    cmd_line_params = []
    for (k,v) in cmd_line_params_dict.items():
        pk = add_dash(k)

        if v == "False":
            continue
        if v == "True":
            cmd_line_params += [pk]
        else:
            cmd_line_params += [pk, v]
    return cmd_line_params 

if __name__ == "__main__":
    seed = sys.argv[5]
    cmd_line_params = ["-parameters", "tune.txt", "-random_seed", seed] + sys.argv[6:]
    cmd_line_params = preprocess_parameters(cmd_line_params)
    set_params(cmd_line_params) 
    start = timer()
    fitness, length = tune()
    duration = int(timer() - start)
    print_results(seed, fitness, duration, length)
    sys.exit(0)
