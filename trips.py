import requests
import json


def osrm_trip(id,x1,y1,x2,y2,mode):

    route_url = "http://127.0.0.1:5000/route/v1/" + mode + "/" + str(x1) + "," + str(y1) + ";" + str(x2) + "," + str(y2) + "?steps=false&geometries=geojson&overview=false"

    print(route_url)

    page = requests.get(route_url)

    route = json.loads(page.content)

    duration = route['routes'][0]['legs'][0]["duration"]
    distance = route['routes'][0]['legs'][0]["distance"]

    print(duration)



def osrm_trip_geojson(id,x1,y1,x2,y2,mode):

    route_url = "http://127.0.0.1:5000/route/v1/" + mode + "/" + str(x1) + "," + str(y1) + ";" + str(x2) + "," + str(y2) + "?steps=false&geometries=geojson&overview=full"

    page = requests.get(route_url)

    route = json.loads(page.content)

    duration = route['routes'][0]['legs'][0]["duration"]
    distance = route['routes'][0]['legs'][0]["distance"]

    geometry = route['routes'][0]["geometry"]

    geojson = {
        "type": "FeatureCollection","features": [
        {
          "type": "Feature",
          "properties": {
            "ID": id,
            "duration": duration,
            "distance": distance
          },
          "geometry": geometry
        }
      ]
    }

    return geojson



osrm_trip(1,-79.24610,43.82540,-79.93925,43.53418,"drive")

g = osrm_trip_geojson(1,-79.24610,43.82540,-79.93925,43.53418,"drive")

with open("test3.geojson", 'w') as fatty_mcgoo:
	json.dump(g, fatty_mcgoo)
