from classes import *
import pandas as pd
from datetime import datetime, timedelta, time

def get_delays():
    #import delays parameters where stop_name is mentionned
    delays_with_stopname_path = '../data/delays.parquet'
    delays_df = pd.read_parquet(delays_with_stopname_path,engine = 'pyarrow')
    
    delays_without_stopname_path = '../data/delays_without_stopname.parquet'
    delays_without_stopname = pd.read_parquet(delays_without_stopname_path,engine = 'pyarrow')
    default_probability_params = {}
    for index, row in delays_without_stopname.iterrows():
        hour_cat = row['hour_cat']
        transport_cat = row['transport_cat']
        param = row['param']
        default_probability_params[(hour_cat, transport_cat)] = param
        
    return delays_df, default_probability_params


def get_stops(delays_df, default_probability_params) :
    stops_path = '../data/stops_radius.parquet'
    stops_df = pd.read_parquet(stops_path, engine = 'pyarrow')
    
    stops = []
    stop_names = set()
    stops_match_id_name = {}

    stop_names_params = delays_df['stop_name'].unique()

    for index, row in stops_df[:].iterrows():
        stop_name = row['stop_name']
        stop_id = row['stop_id']

        stops_match_id_name[stop_id]= stop_name

        if not stop_name in stop_names :
            stop_names.add(stop_name)

            delays_param = {}

            if stop_name in stop_names_params :

                matchine_name_param = delays_df[delays_df['stop_name'] == stop_name]

                for index1, row1 in matchine_name_param.iterrows():
                    hour_cat = row1['hour_cat']
                    transport_cat = row1['transport_cat']
                    param = row1['param']
                    delays_param[(hour_cat, transport_cat)] = param

            else :
                delays_param = default_probability_params

            stops.append(Stop(stop_id, stop_name, row['stop_lat'], row['stop_lon'], set(), list(), delays_param))
    return stops, stops_match_id_name, stops_df


def get_routes(stops, stops_match_id_name):
    def matching_category (transport_type) : 
        train_categories = {'T', 'RE', 'S', 'IC', 'IR', 'KB', 'EC', 'ICE', 'NJ', 'EXT', 'TGV'}
        bus_categories = {'B', 'BAT', 'FUN', 'FAE', 'PB'}

        if transport_type in train_categories:
            return 1
        elif transport_type in bus_categories:
            return 2
        else:
            return None  # Return None or handle other cases as needed
    
    routes_path = '../data/routes.parquet'
    routes_df = pd.read_parquet(routes_path)
    
    routes = []

    #Add each routes to the array
    for index, row in routes_df[:].iterrows():
        route_id  = row['route_id']
        route_opposite_id = route_id +  '-opposite'

        route_transport_type = matching_category(row['route_desc'])

        #For each initial route, we create two routes, the same route but travels in the oppposite sens the stops
        new_route = Route(route_id, route_transport_type, list(), list())
        new_route_opposite = Route(route_opposite_id,route_transport_type , list(), list())

        routes.append(new_route)
        routes.append(new_route_opposite)


        #For each route we traverse we want to indicate to each of the stops this specific route has this stop
        stop_tuples = row['stop_tuples']

        for stop_tuple in stop_tuples :

            stop_id = stop_tuple['stop_id']
            stop_name = stops_match_id_name.get(stop_id)

            if stop_name is not None:

                stop = next(s for s in stops if s.stop_name == stop_name)
                stop.routes.add(new_route)
                stop.routes.add(new_route_opposite)

                #And since we have the reference to the specific stop we also have to add this stop to the two route's list of stops
                new_route.stops_list.append(stop)
                new_route_opposite.stops_list.insert(0,stop)
    for r in routes : 
        t = r.transport
        if t != 1 and t != 2 : 
            print('error')
    return routes

def get_trips(stops, routes, stops_match_id_name):
    def check_stop_order(route_intial, trip_tuples):
        route_names = [stop.stop_name for stop in route_intial.stops_list]
        stops_in_trip = []
        for stop_in_trip in trip_tuples :  
            stop_name = stops_match_id_name.get(stop_in_trip['stop_id'])
            if len(stops_in_trip) >= 2 :
                break
            if stop_name in route_names :
                stops_in_trip.append(stop_name)
        if len(stops_in_trip) == 2 :
            for stop in route_intial.stops_list :
                if stop.stop_name == stops_in_trip[0] :
                    return True
                elif stop.stop_name == stops_in_trip[1] :
                    return False
                
    trips_path = '../data/trips.parquet'
    trips_df = pd.read_parquet(trips_path)
    data_date_format = "%H:%M:%S"

    for index, row in trips_df[:].iterrows():
        new_trip = Trip(row['trip_id'], 'default', {})

        #For each trip we traverse we want to indicate to each of the stops this specific trip has this stop
        trip_tuples = row['trip_tuples']

        #For each tuple of the trip, a tuple represent the stop of the trip and associated times
        for trip_tuple in trip_tuples :

            stop_id = trip_tuple['stop_id']

            stop_name = stops_match_id_name.get(stop_id)

            if not stop_name == None :
                stop = next(s for s in stops if s.stop_name == stop_name)
                departure_time_str = trip_tuple['departure_time']

                # Split the hour string into hours, minutes, and seconds
                hours, minutes, seconds = map(int, departure_time_str.split(':'))

                # Sanity check for valid hour range
                if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:

                    # Convert the hour string to a datetime object
                    departure_time_date_format = datetime.combine(datetime.today().date(), time.fromisoformat(departure_time_str))

                    arrival_time_str = trip_tuple['arrival_time']
                    arrival_time_date_format = datetime.combine(datetime.today().date(), time.fromisoformat(arrival_time_str))

                    new_trip.stops_list[stop.stop_name] = (arrival_time_date_format , departure_time_date_format)

        #Need to update the route
        route_intial = next ((r for r in routes if r.route_id == row['route_id']), None)
        route_opposite_id = row['route_id'] + '-opposite'
        route_opposite = next ((r for r in routes if r.route_id == route_opposite_id), None)

        if not route_intial == None :

            #We need to know in which way the trip is going

            first_trip_stop_name = stops_match_id_name.get(trip_tuples[0]['stop_id'])
            second_trip_stop_name = stops_match_id_name.get(trip_tuples[1]['stop_id'])

            is_order_correct = check_stop_order(route_intial, trip_tuples)

            if is_order_correct :
                new_trip.route_id = route_intial.route_id
                route_intial.trips_list.append(new_trip)
            else :
                new_trip.route_id = route_opposite.route_id
                route_opposite.trips_list.append(new_trip)   


def get_footpaths(stops, routes, stops_match_id_name):
    footpaths_data_path = '../data/walking.parquet'
    footpaths_df = pd.read_parquet(footpaths_data_path)
    footpaths = []
    encountered_footpaths = set()

    #Add each routes to the array
    for index, row in footpaths_df[:].iterrows():

        stopA_id = row['stop_id1']
        stopA_name = stops_match_id_name.get(stopA_id)

        #For each footpath we consider
        reachable_stops = row['reachable_stops']

        for reachable_stop in reachable_stops :

            stopB_id = reachable_stop['stop_id2']
            stopB_name = stops_match_id_name.get(stopB_id)


            #Can have duplicate as a pair can be entered as stopA,stopB and stopB,stopA, need to check if the pair has already been added
            if stopA_name is not None and stopB_name is not None and stopA_name != stopB_name and not ((stopA_name, stopB_name) in encountered_footpaths) and not ((stopB_name, stopA_name) in encountered_footpaths) :

                encountered_footpaths.add((stopA_name, stopB_name))

                walking_time = timedelta(seconds = reachable_stop['walking_time'])
                stopA_ref = None
                stopB_ref = None

                #Need to retrieve the reference to the stops
                for stop in stops:
                    if stop.stop_name == stopA_name:
                        stopA_ref = stop
                    elif stop.stop_name == stopB_name:
                        stopB_ref = stop

                #Update each stop list of footpath
                if stopA_ref != None and stopB_ref != None :
                    stopA_ref.footpaths.append((stopB_ref, walking_time))
                    stopB_ref.footpaths.append((stopA_ref, walking_time))

                    new_footpath = Footpath(stopA_ref, stopB_ref, walking_time)

                    footpaths.append(new_footpath)
    return footpaths
def remove_bad_trips(routes) :
    for route in routes :
        route_names = [stop.stop_name for stop in route.stops_list]
        route_trip_list = []
        for trip in route.trips_list :
            stops_in_trip = []
            for stop,time in trip.stops_list.items() :  
                if len(stops_in_trip) >= 2 :
                    break
                if stop in route_names :
                    stops_in_trip.append(stop)
            if len(stops_in_trip) == 2 :
                for stop in route.stops_list :
                    if stop.stop_name == stops_in_trip[0] :
                        route_trip_list.append(trip)
                        break 
                    elif stop.stop_name == stops_in_trip[1] :
                        # print(f"{route.route_id} {route}")
                        break
        route.trips_list = route_trip_list

def verify_bad_trips(routes):
    for route in routes :
        route_names = [stop.stop_name for stop in route.stops_list]
        for trip in route.trips_list :
            stops_in_trip = []
            for stop,time in trip.stops_list.items() :  
                if len(stops_in_trip) >= 2 :
                    break
                if stop in route_names :
                    stops_in_trip.append(stop)
            if len(stops_in_trip) == 2 :
                for stop in route.stops_list :
                    if stop.stop_name == stops_in_trip[0] :
                        break 
                    elif stop.stop_name == stops_in_trip[1] :
                        print(f"{route.route_id} {route}")
                        raise Exception()
def get_data():
    delays_df, default_probability_params = get_delays()
    stops, stops_match_id_name, stops_df = get_stops(delays_df, default_probability_params)
    routes = get_routes(stops, stops_match_id_name)
    get_trips(stops, routes, stops_match_id_name)
    footpaths = get_footpaths(stops, routes, stops_match_id_name)
    
    # Sanitize the rotutes by sorting the trips and removing trip that should not be in this route
    for route in routes: 
        route.sanitize()
    remove_bad_trips(routes)
    return stops, routes, footpaths, stops_df
