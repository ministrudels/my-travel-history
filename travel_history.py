import reverse_geocoder as rg
import json
import csv
import argparse

from datetime import datetime
from geopy.geocoders import Nominatim
from progressbar import ProgressBar
pbar = ProgressBar()

ACCURACY_LIMIT = 500
EVERY_TH = 60
CSV_file = "travel_history.csv"
JSON_file = "cleaned_locations.json"
HOME = 'TEST HOME'

fieldnames = ['Country', 'Date Arrived', 'Date Departed', 'Duration']
new_json = {
    'locations': []
}

class Person:

    def __init__(self):
        self.currentDatetime = None
        self.currentCountry = {
            "country": None,
            "datetimeArrived": None
        }
        self.confidentLocations = []
        self.travelHistory = []


    def move(self, lat, lon, unixTime, accuracy):
        time = datetime.utcfromtimestamp(int(unixTime)/1000)
        country = rg.search((lat/10000000, lon/10000000))[0]['cc']
        data = {
            "timestampMs": unixTime,
            "time": time.strftime('%Y-%m-%d %H:%M'),
            "latitudeE7": lat,
            "longitudeE7": lon,
            "accuracy" : accuracy,
            "location": country  # default mode = 2
        }
        self.confidentLocations.append(data)

        if self.currentCountry["country"] is None:
            self.currentCountry = {
                "country": country,
                "datetimeArrived": time
            }

        if self.currentCountry["country"] != country:
            self.travelHistory.append({
                "Country": self.currentCountry["country"],
                "Date Arrived": self.currentCountry["datetimeArrived"].strftime('%Y-%m-%d'),
                "Date Departed": time.strftime('%Y-%m-%d'),
                "Duration": (time - self.currentCountry["datetimeArrived"]).days
            })

            self.currentCountry = {
                "country": country,
                "datetimeArrived": time
            }
        self.currentDatetime = time
            
    def getTravelHistory(self):
        if self.currentDatetime != self.currentCountry['datetimeArrived']:
            self.travelHistory.append({
            "Country": self.currentCountry["country"],
            "Date Arrived": self.currentCountry["datetimeArrived"].strftime('%Y-%m-%d'),
            "Date Departed": None,
            "Duration": (self.currentDatetime - self.currentCountry["datetimeArrived"]).days
        })
        return self.travelHistory
        

def printBreak(n):
    print("\n" * n)

def addArgParser():
    parser = argparse.ArgumentParser(description='travel_history.py processes your Google location history to turn it into a well formated travel history document.')
    parser.add_argument('file', help='Google location history file')
    parser.add_argument("--accuracy", default=ACCURACY_LIMIT, help="(Int) Accuracy boundary for Google location data. Defaults to 500")
    parser.add_argument("--every", default=EVERY_TH, help="(Int) Sample everyth datapoint in the file. Defaults to 60")
    parser.add_argument("--home", help="(String) Home country code. See README for table of country codes to their countries")

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = addArgParser()
    ACCURACY_LIMIT = int(args.accuracy)
    EVERY_TH = int(args.every)

    printBreak(2)
    print('Loading location history file into memory....')
    with open(args.file) as json_file:
        data = json.load(json_file)
    print('There are ', len(data['locations']), ' location datapoints from location file...')
    printBreak(1)

    user = Person()
    cleaned_dp = []
    # Chuck out all points with accuracy
    for d in range(len(data['locations'])):
        if data['locations'][d]['accuracy'] > ACCURACY_LIMIT:
            continue
        cleaned_dp.append(data['locations'][d])

    printBreak(2)
    print('Removed datapoints with accuracy >', ACCURACY_LIMIT, 'There are now ', len(cleaned_dp), ' location datapoints')
    print('Taking every', EVERY_TH, 'th datapoint,', len(cleaned_dp[0::EVERY_TH]), 'datapoints to csv and new json')


    # Build person object and run getLocationHistory to get csv file
    for dp in pbar(cleaned_dp[0::EVERY_TH]):
        user.move(dp['latitudeE7'], dp['longitudeE7'], dp['timestampMs'], dp['accuracy'])

    cleaned = user.getTravelHistory()

    with open(CSV_file, 'w', newline='') as csvfile:
        csv_f = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_f.writeheader()
        csv_f.writerows(cleaned)

    with open(JSON_file, 'w') as outfile:
        new_json['locations'] = cleaned
        json.dump(new_json, outfile)
