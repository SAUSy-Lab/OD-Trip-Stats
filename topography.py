import pandas as pd
import geopandas as gpd
import pyrosm
import requests
import json
import time
import csv
import os
import math


# function for getting elevation of coords from geogratis API
def get_elevation(X,Y):
    url = "http://geogratis.gc.ca/services/elevation/cdem/altitude?"
    payload = {"lat": Y, "lon": X}
    page = requests.get(url,params = payload)
    elev = json.loads(page.content)
    return elev["altitude"]


# based on toblers hiking function
def walk_speeds_tobler(slope):

    speed = 6 * math.exp(-3.5 * abs(slope + 0.05))

    return speed


# bike speeds by slope function (still needs to be updated)
def bike_speeds(slope):

    # uphill
    if slope > 0 and slope <= 0.015:
        speed = 15


    elif slope > 0.015 and slope <= 0.03:
        speed = 15 / 1.1

    elif slope > 0.03 and slope <= 0.06:
        speed = 15 / 1.25

    elif slope > 0.06 and slope <= 0.12:
        speed = 15 / 1.5

    elif slope > 0.12:
        speed = 15 / 2

    # downhill
    elif slope < 0 and slope >= -0.015:
        speed = 15

    elif slope < -0.015 and slope >= -0.03:
        speed = 15 / 0.8

    elif slope < -0.03 and slope >= -0.06:
        speed = 15 / 0.9

    elif slope < -0.06 and slope >= -0.12:
        speed = 15 / 1.3

    elif slope < -0.12:
        speed = 15 / 2

    # flat i.e. slope = 0
    else:
        speed = 15

    return speed


# looping over every node in the OSM, getting the get_elevation
# the parameter j, is where to start if the connection times out middway
# data is saved into an "elev" folder
def osm_node_elevations(j = 0):

    # Initialize the OSM object
    osm = pyrosm.OSM("slopes/gtha_2017.pbf")

    # getting nodes and edges
    nodes, edges = osm.get_network(nodes=True, network_type="walking")
    del edges

    # remeoving unneeded columns
    nodes = nodes[["lon","lat","id"]]

    # break into chunks of 100
    osmids = nodes["id"].to_list()
    n_chunks = 1000
    def chunks(lst,n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    osmid_chunks = list(chunks(osmids,n_chunks))

    print(time.time() - start_time)

    # computing elev in chunks because of possibility of api time outs
    # del with rm -rf elevs
    while j < len(osmid_chunks):

        # get the geoids for this chunk
        osmids = osmid_chunks[j]

        # subset the full matrix by this set of geoids
        nodes_sub = nodes[nodes.id.isin(osmids)]


        # empty out array
        dfout = [["id","lon","lat","elev"]]

        for i, row in nodes_sub.iterrows():

            elev = get_elevation(row["lon"],row["lat"])

            outrow = [row["id"],row["lon"],row["lat"],elev]

            dfout.append(outrow)


        with open("slopes/elevs/" + str(j) + "_nodes_elev.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            for row in dfout:
                writer.writerow(row)

        print(pd.DataFrame(dfout))

        j += 1

        print(j, "/", len(osmid_chunks), time.time() - start_time)

        print("------------------------")



# estimating slopes for edges in OSM based on the node elevations computed in the previous function
def osm_slopes():

    start_time = time.time()

    # Initialize the OSM object

    osm = pyrosm.OSM("slopes/gtha_2017.pbf")

    # getting edges

    nodes, edges = osm.get_network(nodes=True, network_type="walking")

    edges1 = edges[['u','v','length','highway',"bridge","tunnel"]]
    edges1.rename(columns = {'u':'i', 'v':'j'}, inplace = True)

    edges2 = edges[['v','u','length','highway',"bridge","tunnel"]]
    edges2.rename(columns = {'v':'i', 'u':'j'}, inplace = True)

    df = pd.concat([edges1, edges2 ], axis=0)

    del edges, edges1, edges2



    # read in elevation data

    dfe = pd.read_csv("slopes/elevs/0_nodes_elev.csv")
    for filename in os.listdir("slopes/elevs"):
        if filename.endswith(".csv"):
            dfe = pd.concat([dfe, pd.read_csv("slopes/elevs/" + filename)], axis = 0)
    dfe = dfe.drop_duplicates()


    # joining data

    df = df.merge(dfe, how="left", left_on='i', right_on="id")
    df.rename(columns = {'elev':'i_elev'}, inplace = True)

    df = df.merge(dfe, how="left", left_on='j', right_on="id")
    df.rename(columns = {'elev':'j_elev'}, inplace = True)

    df = df[["i","j","length", "i_elev","j_elev","highway","bridge","tunnel"]]


    # computing slope

    df["slope"] = (df["j_elev"] - df["i_elev"]) / df["length"]

    df.loc[df.bridge == "yes", 'slope'] = 0
    df.loc[df.tunnel == "yes", 'slope'] = 0
    df.loc[df.highway == "steps", 'slope'] = 9999

    df = df[["i","j","slope"]]

    df.to_csv("slopes/osm_slopes.csv", index = False)



# getting bike speeds for all edges in OSM based on slope
def osm_speeds_bike():

    # load in the slopes and compute speed

    df = pd.read_csv("slopes/osm_slopes.csv")

    df["speed"] = df.slope.apply(bike_speeds)

    # steps to 2km/hr
    df.loc[df.slope == 9999, 'speed'] = 2

    del df["slope"]

    print(df)

    df["speed"] = df["speed"].astype(int)

    df.to_csv("slopes/osm_speeds_bike.csv", index = False, header = False)



# getting walk speeds for all edges in OSM based on slope
def osm_speeds_walk():

    df = pd.read_csv("slopes/osm_slopes.csv")

    df["speed"] = df.slope.apply(walk_speeds_tobler)

    # steps to 2km/hr
    df.loc[df.slope == 9999, 'speed'] = 2.4

    # anything super steep to 1
    df.loc[df.speed < 1, 'speed'] = 1

    # NAs to flat
    df.speed = df.speed.fillna(5)

    del df["slope"]

    df["speed"] = df["speed"].astype(int)

    df.to_csv("slopes/osm_speeds_walk.csv", index = False, header = False)


# osm_speeds_bike()
# osm_speeds_walk()









#
