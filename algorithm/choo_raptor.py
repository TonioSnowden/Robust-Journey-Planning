from datetime import datetime, time, timedelta
from typing import List, Set
from classes import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
from scipy.stats import norm
import math

class ChochocrewAlgorithm : 
    
    def __init__(self, starting_stop : Stop, arrival_stop : Stop, prob_threshold : float,max_arrival_time : datetime, min_arrival_time : datetime, stops : Set[Stop],routes : Set[Route], footpaths : Set[Footpath], verbose : bool = False, with_proba : bool = True) : #The number of minutes before max_arrival_time we can arrive.
        self.MAX_NUMBER_TRANSFERS = 6
        self.MIN_TRANSFER_TIME = timedelta(minutes = 2)
        self.NB_TRIPS_TAKEN_IN_LATEST_ARRIVAL = 2
        
        self.starting_stop = starting_stop
        self.arrival_stop = arrival_stop
        self.prob_threshold = prob_threshold
        self.max_arrival_time = max_arrival_time
        self.stops = stops
        self.routes = routes
        self.footpaths = footpaths
        
        
        diff_time = timedelta(minutes = 1)
        self.arrival_times = [min_arrival_time]
        while self.arrival_times[-1] < max_arrival_time :
            self.arrival_times.append(self.arrival_times[-1] + diff_time)
            
        self.best_journeys = []
        self.marked_stops = set()
        self.verbose = verbose
        self.with_proba = with_proba
        
    def run(self):
        
        for arrival_time in self.arrival_times :
            if self.verbose :
                print(f"\n> Looking for trip arriving at {arrival_time}")
            self.chooRaptor(arrival_time)
        
        journies = self.get_jounrnies()
        return journies
    
    def chooRaptor(self, arrival_time : datetime):
        routes_to_process = set()
        
        self.arrival_stop.label_bags[0].add(Label(self.arrival_stop,arrival_time, 1, None, None, None), self.prob_threshold, self.starting_stop)
        self.marked_stops.add(self.arrival_stop)
        
        for k in range(1, self.MAX_NUMBER_TRANSFERS+1):
            if self.verbose :
                print(f"   > Looking for trip with {k-1} transfers")
            for stop in self.stops:
                stop.update_next_bag(k, self.prob_threshold, self.starting_stop)
            
            routes_to_process = self.get_routes_to_process()
            if self.verbose :
                print(f"      > There are {len(routes_to_process)} route to process")
                
            self.marked_stops = set()
            
            self.process_routes(routes_to_process, k) 
            
            if self.verbose :
                print(f"      > processing footpaths")
            self.process_footpaths(k)
            
            # If we found a stable solution we stop
            if len(self.marked_stops) == 0 :
                break;
                
        
        
    def get_routes_to_process(self):
        """
        Given all the marked stops of the previous round, return all the routes  with the latest stop that we need to process for this round
        
        :marked_stops: a set of stops
        return a dictionnary with route as a key and stop as a value
        """
        routes_to_process = dict()
        for stop in self.marked_stops :
            for route in stop.routes :
                if route in routes_to_process :
                    routes_to_process[route] = route.latest_stop(stop, routes_to_process[route])
                else :
                    routes_to_process[route] = stop
        return routes_to_process
    
    def process_routes(self, routes_to_process, k :int):
        """
        Process all the routes given as argument 
        
        :routes_to_process: dictionnary with a route as value and a stop as key. The stop is the lattest stop of interest in the route
        :k: the round number
        """
        
        for route, last_stop in routes_to_process.items() :
            route_bag = LabelBag(last_stop)
            for stop in route.get_stops_until(last_stop) :
                
                new_label_bag = LabelBag(stop) 
                for label in route_bag.bag :
                    # Updates the arrival time of every labels according to their trip
                    new_label_bag.add(Label(stop,label.trip.time_at_stop(stop, arrival = False),label.prob_to_pt , label.trip, label.get_off_stop, label.next_label), self.prob_threshold, self.starting_stop )
                route_bag = new_label_bag
                #Merge new possible trips with the previous ones    
                stop.label_bags[k], updated = stop.label_bags[k].merge_with(route_bag, self.prob_threshold, self.starting_stop)
                if updated :
                    self.marked_stops.add(stop)
                
                #Update route_bag with routes that we could take a stop p
                new_labels = set()
                for label in stop.label_bags[k-1].bag :
                    # Look at the latest trips we can take to arrive at <stop> before we need to leave <stop>
                    latest_trips = self.latest_arrival(route, stop, label.departure_time, n = self.NB_TRIPS_TAKEN_IN_LATEST_ARRIVAL)
                    #For each of these trip compute a label
                    for trip in latest_trips :
                        if isinstance(label.trip, Footpath) : 
                            new_proba = label.prob_to_pt
                        
                        else : 
                            
                            new_proba = self.compute_proba(arrival_time = trip.time_at_stop(stop),
                                                  departure_time = label.departure_time, #The latest time someone can leave this stop in order to arrive on time at pt according to this label 
                                                  stop = stop, 
                                                  route = route, 
                                                  previous_proba = label.prob_to_pt)
                        new_labels.add(Label(stop, trip.time_at_stop(stop, arrival = False) - self.MIN_TRANSFER_TIME, new_proba, trip, stop, label))

                # Merge the possible new labels with the ones already existing
                route_bag, _ = route_bag.merge_with(LabelBag(stop, new_labels), self.prob_threshold, self.starting_stop)
                              
    def process_footpaths(self, k :int ) :
        """
        Process all the footpaths of going from and to marked stops and update other stops accordingly.
        :k: the current round
        """
        if k ==1 :
            self.marked_stops.add(self.arrival_stop)
        newly_marked_stops = set(self.marked_stops)
        for stop in self.marked_stops :
            for previous_stop, footpath_time in stop.footpaths :
                if previous_stop not in self.stops :
                    continue
                new_labels = set()
                for label in stop.label_bags[k].bag :
                    new_labels.add(Label(previous_stop, label.departure_time - footpath_time, label.prob_to_pt, #0.99 is to escape from waiting loops
                                        Footpath(previous_stop, stop, footpath_time), stop, label
                                        ))
                previous_stop.label_bags[k], updated = previous_stop.label_bags[k].merge_with(LabelBag(previous_stop, new_labels), self.prob_threshold, self.starting_stop)
                if updated :
                    newly_marked_stops.add(previous_stop)
        self.marked_stops = newly_marked_stops
        
        
    
    def latest_arrival(self, route : Route, stop : Stop, time : datetime, n :int = 3) :
        """
        Gives the latest n trips of route r that we can take at stop p before time 

        :route: the Route of interest
        :stop: the stop of interest
        :time: the maximum time at which the trip must arrive at <stop>
        :n: the number of trip arriveing before time at stop p we want 
        :return: the max n latest trips of route r in increasing time order that we can take at stop p before time. If there are less than n trips before time t then less trips are returned
        """ 
        # We go through the trips of the route in decreasing order
        possible_trips = []
        max_diff_time = timedelta(hours = 1, minutes = 10)
        for i, trip in enumerate(route.trips_list) :
            time_at_stop = trip.time_at_stop(stop)
            if time_at_stop != None and time_at_stop > time -max_diff_time and time_at_stop <= time : 
                possible_trips.append(trip)
        
        
        possible_trips = sorted(possible_trips, key=lambda trip : 
            trip.time_at_stop(stop))
        
        return possible_trips[max(0, len(possible_trips)-n) :]
    
    
    def compute_proba(self, arrival_time :datetime, departure_time:datetime, stop :Stop, route:Route, previous_proba:float):
        """
        Given arrival time and departure time, compute the proba of sucessfully take the next trip and multiply it with the previous proba 
        
        :arrival_time: the time at which the previous trip arrive at <stop>
        :departure_time: the time at which the next trip leave <stop>
        :stop: the stop of interest
        :route: the route of interest
        :previous_proba: the previous proba
        return the new probability at stop p to arrive at pt using this trip
        """
        if arrival_time == None :
            print("compute proba problem ")
            
        # default_transfer_time_minutes = 2
        # time_delta = timedelta(minutes=default_transfer_time_minutes)
        
        hour_arrival_time = arrival_time.hour
        time_category = 0
        
        if hour_arrival_time in [7, 17, 8]:
            time_category = 1
        elif hour_arrival_time in [16, 18, 19]:
            time_category = 2
        else:
            time_category = 3 
            
        distribution_param = stop.delays_param[(time_category, route.transport)]
        
        w = distribution_param [0]
        gamma_a = distribution_param [4]
        gamma_loc = distribution_param [3]
        gamma_scale = distribution_param[5]
        
        norm_loc = distribution_param[1]
        norm_scale = distribution_param[2]
        
        x = (departure_time - arrival_time).total_seconds()
        
        success_proba = w *  gamma.cdf(x, a=gamma_a, loc=gamma_loc, scale=gamma_scale) + (1 - w ) * norm.cdf(x, loc=norm_loc, scale=norm_scale)

        result = success_proba * previous_proba if self.with_proba else previous_proba
        return min(round(result, 4), 1)
    
    
    def get_jounrnies(self):
        journies = []
        for label in self.starting_stop.label_bags[-1].get_pareto_set() : # the -1 may be wrong
            # print(label)
            journey = []
            stop = self.starting_stop
            new_label = label
            nb_transfers = 0
            while new_label.next_label != None :
                if type(new_label.trip) == Footpath : #If we need to take a foot_path
                    journey.append((new_label.departure_stop.stop_name, #start_point
                                new_label.get_off_stop.stop_name, #end_point
                                new_label.departure_time, #start time
                                new_label.departure_time + new_label.trip.time, #arrival time
                                "Walk")) #walking time
                else : 
                    type_of_transp = [route for route in self.routes if route.route_id == new_label.trip.route_id][0].transport
                    type_of_transp = "Train" if type_of_transp == 1 else "Bus"
                    journey.append((new_label.departure_stop.stop_name, #start_point
                                new_label.get_off_stop.stop_name, #end_point
                                new_label.trip.time_at_stop(new_label.departure_stop, arrival = False), #start time
                                new_label.trip.time_at_stop(new_label.get_off_stop), #arrival time
                                type_of_transp)) #walking time
                    nb_transfers +=1
                # Update
                new_label = new_label.next_label
                stop = label.get_off_stop
            journies.append({
                'journey' : journey,
                'proba' : round(label.prob_to_pt * 100, 2),
                'departure_time' : journey[0][2],
                'arrival_time' : journey[-1][3],
                'nb_transfers' : max(nb_transfers-1,0)
            })
            
            
        return sorted(journies, key=lambda x: x['departure_time'], reverse=True) 
