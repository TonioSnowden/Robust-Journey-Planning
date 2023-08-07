from choo_raptor import ChochocrewAlgorithm
from classes import *
import pandas as pd
from datetime import datetime, timedelta, time

def test1(stops, routes, footpaths):# Test 1 
    # Two close stops without changes 
    starting_stop_name_t1 = 'Baar, Ruessen'
    arrival_stop_name_t1 = 'Baar, Walterswil'

    starting_stop_t1 = [stop for stop in stops if stop.stop_name.lower() in starting_stop_name_t1.lower()][0]
    arrival_stop_t1 = [stop for stop in stops if stop.stop_name.lower() in arrival_stop_name_t1.lower()][0]

    prob_threshold_t1 = 0.0
    max_arrival_time_str_t1 = '12:48:00'
    max_arrival_time_t1 = datetime.combine(datetime.today().date(), time.fromisoformat(max_arrival_time_str_t1))
    min_arrival_time_str_t1 = '12:48:00'
    min_arrival_time_t1 = datetime.combine(datetime.today().date(), time.fromisoformat(min_arrival_time_str_t1))
    # Reset all the lists
    choo_algo = ChochocrewAlgorithm(starting_stop = starting_stop_t1,
                                    arrival_stop = arrival_stop_t1, 
                                    prob_threshold = prob_threshold_t1,
                                    max_arrival_time = max_arrival_time_t1, 
                                    min_arrival_time = min_arrival_time_t1,
                                    stops = stops,
                                    routes = routes, 
                                    footpaths = footpaths,
                                    verbose = False,
                                    with_proba = True
                                   )
    for stop in stops :
        stop.label_bags = [LabelBag(stop)]
    return choo_algo.run()

def test1_2(stops, routes, footpaths):
    # Test 1.2 
    # Two close stops without changes but with the route in the other way
    starting_stop_name_t1_2 = 'Baar, Walterswil'
    arrival_stop_name_t1_2 = 'Baar, Pfaffentobel'

    starting_stop_t1_2 = [stop for stop in stops if stop.stop_name.lower() in starting_stop_name_t1_2.lower()][0]
    arrival_stop_t1_2 = [stop for stop in stops if stop.stop_name.lower() in arrival_stop_name_t1_2.lower()][0]

    prob_threshold_t1_2 = 0.5 
    max_arrival_time_str_t1_2 = '12:50:00'
    max_arrival_time_t1_2 = datetime.combine(datetime.today().date(), time.fromisoformat(max_arrival_time_str_t1_2))
    min_arrival_time_str_t1_2 = '12:30:00'
    min_arrival_time_t1_2 = datetime.combine(datetime.today().date(), time.fromisoformat(min_arrival_time_str_t1_2))

    choo_algo = ChochocrewAlgorithm(starting_stop = starting_stop_t1_2,
                                    arrival_stop = arrival_stop_t1_2, 
                                    prob_threshold = prob_threshold_t1_2,
                                    max_arrival_time = max_arrival_time_t1_2, 
                                    min_arrival_time = min_arrival_time_t1_2,
                                    stops = stops,
                                    routes = routes, 
                                    footpaths = footpaths,
                                    verbose = False,
                                   with_proba = True)
    for stop in stops :
        stop.label_bags = [LabelBag(stop)]
    return choo_algo.run()

def test2(stops, routes, footpaths):
    starting_stop_name_t2 = 'Dietikon'
    arrival_stop_name_t2 = 'Zürich Flughafen'

    starting_stop_t2 = [stop for stop in stops if stop.stop_name.lower() in starting_stop_name_t2.lower()][0]
    arrival_stop_t2 = [stop for stop in stops if stop.stop_name.lower() in arrival_stop_name_t2.lower()][0]

    prob_threshold_t2 = 0.0
    max_arrival_time_str_t2 = '12:23:00'
    max_arrival_time_t2 = datetime.combine(datetime.today().date(), time.fromisoformat(max_arrival_time_str_t2))
    min_arrival_time_str_t2 = '12:21:00'
    min_arrival_time_t2 = datetime.combine(datetime.today().date(), time.fromisoformat(min_arrival_time_str_t2))

    choo_algo = ChochocrewAlgorithm(starting_stop = starting_stop_t2,
                                    arrival_stop = arrival_stop_t2, 
                                    prob_threshold = prob_threshold_t2,
                                    max_arrival_time = max_arrival_time_t2, 
                                    min_arrival_time = min_arrival_time_t2,
                                    stops = stops,
                                    routes = routes, 
                                    footpaths = footpaths,
                                    verbose = False, 
                                   with_proba = True)
    for stop in stops :
        stop.label_bags = [LabelBag(stop)]
    return choo_algo.run()

def test3(stops, routes, footpaths):
    starting_stop_name_t4 = 'Zürich, Zoo'
    arrival_stop_name_t4 = 'Zürich Oerlikon'

    starting_stop_t4 = [stop for stop in stops if stop.stop_name.lower() in starting_stop_name_t4.lower()][0]
    arrival_stop_t4 = [stop for stop in stops if stop.stop_name.lower() in arrival_stop_name_t4.lower()][0]

    prob_threshold_t4 = 0.0
    max_arrival_time_str_t4 = '15:00:00'
    max_arrival_time_t4 = datetime.combine(datetime.today().date(), time.fromisoformat(max_arrival_time_str_t4))
    min_arrival_time_str_t4 = '14:55:00'
    min_arrival_time_t4 = datetime.combine(datetime.today().date(), time.fromisoformat(min_arrival_time_str_t4))


    choo_algo = ChochocrewAlgorithm(starting_stop = starting_stop_t4,
                                    arrival_stop = arrival_stop_t4, 
                                    prob_threshold = prob_threshold_t4,
                                    max_arrival_time = max_arrival_time_t4, 
                                    min_arrival_time = min_arrival_time_t4,
                                    stops = stops,
                                    routes = routes, 
                                    footpaths = footpaths,
                                    verbose = False,
                                   with_proba = True)
    for stop in stops :
        stop.label_bags = [LabelBag(stop)]
    return choo_algo.run()

def test4(stops, routes, footpaths):
    starting_stop_name_t4 = 'Zürich, Zoo'
    arrival_stop_name_t4 = 'Zürich Flughafen'

    starting_stop_t4 = [stop for stop in stops if stop.stop_name.lower() in starting_stop_name_t4.lower()][0]
    arrival_stop_t4 = [stop for stop in stops if stop.stop_name.lower() in arrival_stop_name_t4.lower()][0]

    prob_threshold_t4 = 0.0
    max_arrival_time_str_t4 = '15:00:00'
    max_arrival_time_t4 = datetime.combine(datetime.today().date(), time.fromisoformat(max_arrival_time_str_t4))
    min_arrival_time_str_t4 = '15:00:00'
    min_arrival_time_t4 = datetime.combine(datetime.today().date(), time.fromisoformat(min_arrival_time_str_t4))


    choo_algo = ChochocrewAlgorithm(starting_stop = starting_stop_t4,
                                    arrival_stop = arrival_stop_t4, 
                                    prob_threshold = prob_threshold_t4,
                                    max_arrival_time = max_arrival_time_t4, 
                                    min_arrival_time = min_arrival_time_t4,
                                    stops = stops,
                                    routes = routes, 
                                    footpaths = footpaths,
                                    verbose = False,
                                   with_proba = True)
    for stop in stops :
        stop.label_bags = [LabelBag(stop)]
    return choo_algo.run()
