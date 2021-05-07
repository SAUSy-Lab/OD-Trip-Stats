import pandas as pd
import geopandas as gpd
import pyrosm
import requests
import json
import time
import csv

start_time = time.time()

# function for getting elevation of coords from geogratis API
def get_elevation(X,Y):
    url = "http://geogratis.gc.ca/services/elevation/cdem/altitude?"
    payload = {"lat": Y, "lon": X}
    page = requests.get(url,params = payload)
    elev = json.loads(page.content)
    return elev["altitude"]


# Initialize the OSM object
osm = pyrosm.OSM("gtha_2017.pbf")

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
j = 1359
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


    with open("elevs/" + str(j) + "_nodes_elev.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for row in dfout:
            writer.writerow(row)

    print(pd.DataFrame(dfout))

    j += 1

    print(j, "/", len(osmid_chunks), time.time() - start_time)

    print("------------------------")
