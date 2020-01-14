import json
import csv


JSON_data = "min_location_history.json"
CSV_file = "cleaned.csv"
fieldnames = ['timestampMs', 'latitudeE7', 'longitudeE7', 'accuracy']
new_json = {
    'locations': []
}

if __name__ == "__main__":
    cleaned = []

    print('Loading location history file into memory....')
    with open(JSON_data) as json_file:
        data = json.load(json_file)

    print('There are ', len(data['locations']), ' location datapoints. Writing data to csv and new json')
    # Build objects
    for dp in data['locations']:
        row = {
            'timestampMs': dp['timestampMs'],
            'latitudeE7': dp['latitudeE7'],
            'longitudeE7': dp['longitudeE7'],
            'accuracy' : dp['accuracy']
        }
        cleaned.append(row)

    # Write to csv
    with open(CSV_file, 'w', newline='') as csvfile:
        csv_f = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_f.writeheader()
        csv_f.writerows(cleaned)

    # Write to json file

    with open('min_location_history_clean.json', 'w') as outfile:
        new_json['locations'] = cleaned
        json.dump(new_json, outfile)
