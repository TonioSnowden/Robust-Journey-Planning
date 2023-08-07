import pandas as pd
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Define all the functions needed for the interface


def plot_trip(lon, lat, title, names, stops_df):
    fig = px.scatter_mapbox(stops_df, lat="stop_lat", lon="stop_lon", hover_name='stop_name',zoom=12, width=1200, height=900, center={'lon':lon[0],'lat':lat[0]})

    fig.add_trace(go.Scattermapbox(
        name = title,
        mode = "lines+markers",
        text= names[1:],
        lon = lon,
        lat = lat,
        hoverinfo="text",
        marker = {'size': 10}))
    
    fig.add_trace(go.Scattermapbox(
        name = title,
        mode = "markers",
        text= [names[1], names[-1]],
        lon = [lon[0], lon[-1]],
        lat = [lat[0], lat[-1]],
        hoverinfo = "text",
        marker = {'size': 15, 'color': 'aqua'}))

    fig.update_layout(mapbox_style="open-street-map")
    fig.show()

    
def process_journey(journey_tuples, stops_df):
    lon = []
    lat = []
    names = ['']
    for step in journey_tuples:
        if step[0] != names[-1]:
            names.append(step[0])
            lon.append(stops_df[stops_df['stop_name'] == step[0]]['stop_lon'].values[0])
            lat.append(stops_df[stops_df['stop_name'] == step[0]]['stop_lat'].values[0])
        names.append(step[1])
        lon.append(stops_df[stops_df['stop_name'] == step[1]]['stop_lon'].values[0])
        lat.append(stops_df[stops_df['stop_name'] == step[1]]['stop_lat'].values[0])
    return lon, lat, names

def plot_journey(output, nb):
    
    # Extract journey details from the output dictionary
    item = output
    journey_data = []
    for t in range(len(item['journey'])):
        journey = item['journey'][t]
        departure = journey[0]
        arrival = journey[1]
        departure_time = journey[2]
        arrival_time = journey[3]
        transport_type = journey[4]

        journey_data.append({'Departure': departure,
                             'Arrival': arrival,
                             'Departure Time': departure_time.time().strftime('%H:%M'),
                             'Arrival Time': arrival_time.time().strftime('%H:%M'),
                             'Travel Time': (datetime(1, 1, 1) + (arrival_time - departure_time)).strftime('%H:%M'),
                             'Transport type': transport_type})
    nb_transfers = item['nb_transfers']
    proba = item['proba']

    # Create DataFrame from the journey_data list
    df = pd.DataFrame(journey_data)

    print("Journey {} leaves at {} and has a probability of {}% of success with {} transfer(s)".format(nb+1, item['journey'][0][2].time().strftime('%H:%M'), proba, nb_transfers))
    display(df)
    