osrm-extract toronto_test_2021.osm.xml -p bicycle.lua

osrm-contract gtha_2017_car.osrm
osrm-contract toronto_test_2021.osrm --segment-speed-file test_speeds.csv

osrm-routed --max-table-size=3000 gtha_2017_car.osrm


