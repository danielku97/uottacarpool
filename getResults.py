import sys
import math
import time
import googlemaps
import json
import heapq

APPROX_FACTOR = 2
SPEED_LIMIT = 100
_start = 0
_end = 1
_timeRange = 2
_id = 3
gmaps = googlemaps.Client(key='AIzaSyBp_rJUgCdnwC2bAgMLYFMG32GR_eriY58')

# Haversine distance - this is in km
def haver_dist(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

# How much more costly it is for our driver to pick up passenger using haversine heuristic approximation
def calculate_haver_cost(driver, passenger):
    return haver_dist(driver[_start], passenger[_start]) + haver_dist(passenger[_start], passenger[_end]) \
        + haver_dist(passenger[_end], driver[_end]) - haver_dist(driver[_start], driver[_end])

# Distance calculated according to Google Maps API - this is a time, in minutes
# origin and destination are (latitude, longitude)
def real_dist(origin, destination):
    jsonAnswer = gmaps.distance_matrix(origin, destination)
    print(jsonAnswer, "\n\n")
    try: 
        value = jsonAnswer["rows"][0]["elements"][0]["duration"]["value"]
        return value
    except (ValueError, TypeError, KeyError): 
        return -9999999

# How much more costly it is for our driver to pick up passenger using Google Maps API
def calculate_real_cost(driver, passenger):
    print("Now calculating real cost for passenger", passenger[_id])
    return real_dist(driver[_start], passenger[_start]) + real_dist(passenger[_start], passenger[_end]) + \
        real_dist(passenger[_end], driver[_end]) - real_dist(driver[_start], driver[_end])

# Used in the sorting
def distance_value(entry):
    return entry[1]

# Returns the difference in minutes of time1 - time2, both represented in 24h clock, string form: hh:mm
def time_difference(time1, time2):
    hours1, minutes1 = time1.split(":")
    hours2, minutes2 = time2.split(":")
    return 60 * (int(hours1) - int(hours2)) + (int(minutes1) - int(minutes2)) 

# Locations are tuples (latitude, longitude)
# Passengers is a list of passenger. 
# A single driver and passenger both are in the form [start, end, timeRange, id]:
# start and end are both Locations - indicates starting and ending locations
# timeRange is a pair of strings, in 24h format: [hh:mm, hh:mm]. 
# These correspond to the start and end times allowed by the driver or passenger.
def find_passengers(driver, passengers, count):    
    list1 = [] # in list1 we order the passengers by their heuristic cost for our drivers
    list2 = [] # in list2 we take the least costly passengers from list1 and order them by real cost
    for passenger in passengers:
        # Haversine distances here
        dist = calculate_haver_cost(driver, passenger) 
        if dist > APPROX_FACTOR * haver_dist(driver[_start], driver[_end]): 
            print("Heuristic approximate cost is too high for passenger", passenger[_id])
            continue
        # timeDifference is the difference in minutes between the passenger's earliest time 
        # and driver's latest time
        timeDifference = time_difference(driver[_timeRange][1], passenger[_timeRange][0])
        # If the driver's latest time is later than the passenger's earliest time   
        if (timeDifference < 0):
            print("Earliest time is too late for passenger", passenger[_id])
            continue
        if (driver[_end] != passenger[_end]):
        # If the driver's latest time minus passenger's earliest time doesn't give enough time to go from 
        # passenger's end destination to the driver's end destination, they are incompatible.
            if (SPEED_LIMIT/60.0) * (timeDifference) < haver_dist(driver[_end], passenger[_end]):
                print("Not enough time for driver to reach destination after dropping off passenger", passenger[_id])
                continue
        list1.append([passenger, dist])
    list1.sort(key=distance_value)

    for i in range(min(3 * count, len(list1))):
        passenger = list1[i][0]
        # calculate Google Maps distances:
        dist = calculate_real_cost(driver, passenger)
        if dist >= 0:
            list2.append([passenger, dist])
    list2.sort(key=distance_value)
    # Return a list of the passengers and time delays
    return [list2[i] for i in range(min(count, len(list2)))]


def getDriver(driversJson):
    driver = []
    (startlat, startlon) = driverJson["start_coord"][0], driverJson["start_coord"][1]
    (endlat, endlon) = driverJson["end_coord"][0], driverJson["end_coord"][1]
    driver.append((startlat, startlon))
    driver.append((endlat, endlon))
    driver.append(driversJson["arrival_time"])
    driver.append(driverJson["email"])
    return driver

def getPassengers(passengersJson):
    passengers = []
    for passengerJson in passengersJson:
        passenger = []
        (startlat, startlon) = passengerJson["start_coord"][0], passengerJson["start_coord"][1]
        (endlat, endlon) = passengerJson["end_coord"][0], passengerJson["end_coord"][1]
        passenger.append((startlat, startlon))
        passenger.append((endlat, endlon))
        passenger.append(passengerJson["arrival_time"])
        passenger.append(passengerJson["email"])
        passengers.append(passenger)
    return passengers

if __name__ == '__main__':
    count = 10
    # if len(sys.argv) == 2:
    #     if (sys.argv[1]).is_integer():
    #         count = sys.argv[1]
    #testDriver = [(45.4214297,-75.6837206), (44.4748057,-79.9425542), ["11:03", "12:04"], "frcheng"]
    #testPassengers = []
    #testPassenger1 = [(45.42,-75.683), (44.474,-80.542), ["13:03", "16:04"], "lucylu"]
    #testPassenger2 = [(45.4,-75.6), (44.47,-79), ["9:03", "16:04"], "danielku"]
    #testPassenger3 = [(45.62,-76), (45,-79), ["9:03", "16:04"], "jennyzhang"]
    #testPassengers.append(testPassenger1)
    #testPassengers.append(testPassenger2)
    #testPassengers.append(testPassenger3)
    #values = find_passengers(testDriver, testPassengers, count)
    #print(values, "\n\n\n")
    
    # sys.argv[1] is driver json, sys.argv[2] is passengers list json
    driverJson = json.loads(sys.argv[1])
    passengersJson = json.loads(sys.argv[2])
    driver = getDriver(driverJson)
    passengers = getPassengers(passengersJson)

    values = find_passengers(driver, passengers, count)
    # The result type should be a json object
    jsret = json.dumps([{'id': value[0][_id], 'cost': value[1], 'startcoord': value[0][_start], 'endcoord': value[0][_end]} for value in values], indent=4)
    print(jsret)






