osmconvert network_data/gtha_2017.pbf > network_data/gtha_2017_car.osm.xml

osrm-extract drive/gtha_2017_car.osm.xml -p drive/car.lua

rm drive/gtha_2017_car.osm.xml

osrm-contract drive/gtha_2017_car.osrm

osrm-routed drive/gtha_2017_car.osrm
