from datetime import datetime
from typing import List, Set, Dict

class Stop : 
    def __init__(self, stop_id: str, stop_name : str, stop_lat : float, stop_lon: float, routes : Set, footpaths: List, delays_param): 
        """
        stop_id: int: the stop id that is unique, 
        stop_lat : float the stop lattitude,
        stop_lon: float the stop longitude, 
        routes : Set['Route'] the routes that go by this stop, 
        footpaths: List[(Stop,datetime)]: all the footpaths from self to another stop. The keys of the dictionnary are the stop we can go by foot from this stop and the values are the time it takes to do it
        delays_param: the delay parameters 
        """
        self.stop_id  = stop_id 
        self.stop_name  = stop_name 
        self.stop_lat  = stop_lat
        self.stop_lon = stop_lon
        self.routes = routes
        self.footpaths = footpaths # dict stop reachable by foot form this stop with time associated
        self.delays_param = delays_param
        
        self.label_bags = [LabelBag(self)]
        
    def __eq__(self, obj):
        return isinstance(obj, Stop) and obj.stop_name == self.stop_name
    
    def __hash__(self):
        return hash((self.stop_id, self.stop_name , self.stop_lat , self.stop_lon))
    def __str__(self):
        return self.stop_name
    def update_routes(self, routes : List['Route']):
        self.routes = routes
        
    def update_footpaths(self, footpaths):
        self.footpaths = footpaths
        
        
    def update_next_bag(self, k : int, prob_threshold : float, starting_stop :'Stop'):
        """
        Create next bag from previous as an upper bound
        
        :k: the round we are in
        """
        if len(self.label_bags) < k+1: #means that it has length k
            #Then we just copy from previous round
            self.label_bags.append(self.label_bags[-1].copy())
            
        else :
            self.label_bags[k], _ = self.label_bags[k].merge_with(self.label_bags[k-1], prob_threshold, starting_stop)


class Trip : 
    def __init__ (self, trip_id, route_id, stops_list) : 
        self.trip_id : str = trip_id
        self.route_id : str = route_id
        #list of stops, their arrival time and departure time
        self.stops_list : Dict[str, (datetime, datetime)] = stops_list
        
    def __str__(self):
        return ', '.join([f"{stop} : {time[0]}" for stop, time in self.stops_list.items()]) 
        
    def time_at_stop(self, stop : Stop, arrival = True) :
        """
        Given a stop in the trip, return the time at which the trip arrives at this stop
        :stop: a Stop
        return the time the trip arrives at <stop>
        """
        if stop.stop_name in self.stops_list :
            return self.stops_list[stop.stop_name][0 if arrival else 1]
        else :
            return None
    
    def sanitize(self):
        pass



class Footpath : 
    def __init__ (self, stopA, stopB, time) : 
        
        #the two stops for the path and the duration of the path
        
        self.stopA : Stop = stopA 
        self.stopB : Stop = stopB
        self.time : Datetime = time

class Route : 
    def __init__(self, route_id , transport_type : str, stops_list : List , trips_list: List ) : 
        """
        route_id: int : the unique id of the route, 
        transport_type : str : the type of transport. Can be 'train' 'bus' or ????????,
        stops_list : List[Stop]: the list of stops associated to the route in INCREASING order (start stop is first, last stop is last)
        trips_list: List[Trip] : the list of trip associated to the route in time INCREASING order (first trip of the day is first, last trip of the day is last  
        """
        self.route_id  = route_id
        self.transport = transport_type
        self.stops_list = stops_list 
        self.trips_list = trips_list
    
    
    def __str__(self):
        return ', '.join([f"\"{stop.stop_name}\"" for stop in self.stops_list])
    def latest_stop(self, stop1 : Stop, stop2 :Stop) -> Stop:
        """
        Given two stops, return the stop that is the latest in this route
        """
        if stop1 not in self.stops_list :
            print(f"{stop1.stop_name} not in the list ")
        if stop2 not in self.stops_list :
            print(f"{stop2.stop_name} not in the list ")
        for stop in self.stops_list:
            if stop == stop1 :
                return stop2
            elif stop == stop2 :
                return stop1
    
    def get_stops_until(self, stop : Stop):
        """
        Given a stop on the route, returns a list of stop from starting_stop to p (included) in reverse order ([p, ..., p2,p1,p0])
        """
        index = self.stops_list.index(stop)
        return self.stops_list[:index+1][::-1]
    
    def sanitize(self):
        #remove trips of length <2
        self.trips_list = [trip for trip in self.trips_list if len(trip.stops_list) >=2]
        
        #put the trips in increasing order
        self.trips_list = sorted(self.trips_list, key=lambda trip : 
            list(trip.stops_list.items())[0][1][0])

class Label :
    def __init__(self, 
                departure_stop : Stop,
                departure_time : datetime,
                prob_to_pt : float, 
                trip : Trip, 
                get_off_stop : Stop, 
                next_label : 'Label' 
                 ) :
        """
        :departure_time: datetime,#The latest time someone can leave this stop in order to arrive on time at pt according to this label 
        :prob_to_pt: float, Probability of arriving at pt taking this trip
        :trip : Trip, The trip we need to take form this stop
        :get_off_stop:Stop, The stop we must get off this trip to take another trip
        :next_label : Label, Next label at stop <get_off_stop>
        """
        self.departure_stop = departure_stop
        self.departure_time = departure_time
        self.prob_to_pt = prob_to_pt
        self.trip = trip
        self.get_off_stop = get_off_stop
        self.next_label = next_label
        
    def __str__(self):
        if isinstance(self.trip, Trip) :
            return f"ds:{self.departure_stop} at {self.departure_time}, gos {self.trip.time_at_stop(self.get_off_stop) if self.get_off_stop != None else None} at {self.get_off_stop.stop_name if self.get_off_stop != None else None} proba {self.prob_to_pt}"
        else :
            return f"footpath :{self.departure_stop}  {self.get_off_stop} {self.departure_time}"
    
    def copy(self) -> 'Label' :
            return Label(self.departure_stop, self.departure_time, self.prob_to_pt, self.trip, self.get_off_stop, self.next_label)

class LabelBag :
    def __init__(self, departure_stop : Stop, init_labels : List[Label] = []):
        init_labels = [label for label in init_labels if label.departure_time != None ]
        self.bag = list(init_labels)
        self.departure_stop = departure_stop
    
    def __len__(self):
        return len(self.bag)
    
    def add(self, new_label : Label, prob_threshold : float, starting_stop :Stop):
        """
        Given a new label, return a Pareto set of non dominating set of labels.
        1. The new label is not added if <prob_to_pt> and <time> are both equals or both smaller 
        2. If the new label is added then we remove previous element in the set that have <prob_to_pt> and <time> smaller than new label 
        Note that if the new label is not added then it does not remove any label
        
        return Boolean : True if there was an update (the new label was added), False otherwise 
        """
        
                
        # if self.departure_stop.stop_name == "Baar, Ruessen":
        #     print(new_label)
        # If the proba of the label is lower than the threshold we do not add the label
        if new_label.prob_to_pt < prob_threshold :
            return False
        if new_label.departure_time == None :
            return False
        if new_label.get_off_stop != None and isinstance(new_label.trip, Trip) and new_label.departure_time > new_label.trip.time_at_stop(new_label.get_off_stop) :
            return False
        #     raise Exception(f"not possible {new_label}, route id {new_label.trip.route_id}, trip id { new_label.trip.trip_id}")
        
        # We first verify that this label is not beaten by some of the labels already presentin the strating stop 
        for label in starting_stop.label_bags[-1].bag :
            if new_label.prob_to_pt <= label.prob_to_pt and\
                new_label.departure_time <= label.departure_time :
                return False
        
        # We then verify if it is possible to insert it in this bag
        for label in self.bag :
            # If the label is dominated by another label then we do not add it and return
            if new_label.prob_to_pt <= label.prob_to_pt and\
                new_label.departure_time <= label.departure_time :
                return False
            #If the new_label dominates another label then we remove this label and the new_label will eventually be added 
            elif label.prob_to_pt <= new_label.prob_to_pt and\
                label.departure_time <= new_label.departure_time :
                self.bag.remove(label)
                # print(f"remove {label} with {new_label}")
        
        self.bag.append(new_label)

        if new_label.departure_time == None :
            raise Exception("Adding None label")
        return True
        
    def merge_with(self, other : 'LabelBag', prob_threshold : float, starting_stop : Stop):
        """
        Given another bag of labels (already a Pareto dominated set), return a set with no two label where one dominate the other which is equivalent to a Pareto Set.

        :label_bag_1: 
        :label_bag_2: 
        :return: 
            - a LabelBag 
            - if the LabelBag was updated
        """ 
        
        # for label in self.bag :
        #     if label.departure_time == None :
        #         raise Exception("Creating bag of label with None label")
        updated = False
        for label in other.bag :
            result = self.add(label, prob_threshold,starting_stop)
            if result :
                updated = True
            # if label.departure_stop.stop_name == 'Zürich, Bahnhofquai/HB' :
            #     print(label, result)
        return self.copy(), updated
        
    def get_pareto_set(self):
        final = []
        length = len(self.bag)
        bag = self.bag.copy()
        for i in range(length) :
            add = True
            for j in range(length):
                if i != j :
                    # print(bag[i], bag[j])
                    # print(bag[i].prob_to_pt <= bag[j].prob_to_pt, bag[i].departure_time <= bag[j].departure_time)
                    if bag[i].prob_to_pt <= bag[j].prob_to_pt and\
                        bag[i].departure_time <= bag[j].departure_time :
                        add = False
            if add :
                final.append(bag[i])
            
        return final
                
    def copy(self):
        """
        deep_copy of self
        """
        new_labels = set()
        for label in self.bag :
            new_labels.add(label.copy())
        return LabelBag(self.departure_stop, init_labels = new_labels)


