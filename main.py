import re
import requests
import os
import querydata
import postpro
import json
import slackbot
import sys

secrets = json.load(open("secrets.json"))
username = secrets["username"]
password = secrets["password"]

blades = ['V040', 'V015']

if len(sys.argv) < 2:
    print("Must specify blade, for example V040")
    exit()

blade = sys.argv[1]

if blade not in blades: print("Not a valid blade."); exit()

def threshold(data):
    for item in data.prob:
        if item > .99: 
            print(item)
            return True
    return False

# Return the dataframe of the data from the last 5 minutes, saved to output_data.csv
# Return an array of smoke objects, each contain a timestamp, 2d array of smoke probabilites, 
# and https links to current and past images.
if blade == 'V040': smokearray, df = querydata.getdata(3, 6, "registry.sagecontinuum.org/iperezx/wildfire-smoke-detection:0.5.0", "V040")
elif blade == 'V015': smokearray, df = querydata.getdata(3, 6, "registry.sagecontinuum.org/iperezx/wildfire-smoke-detection:0.7.3", "V015")

# Write the DataFrame to a CSV file with minute accuracy and zero seconds
output_file = "output_data.csv"
df.to_csv(output_file, index=False)

newestRes = None
for item in smokearray:
    if newestRes is None or item.timestamp > newestRes.timestamp:
        #if threshold(item):
        newestRes = item

if newestRes is None or not threshold(newestRes):
    print("No data in the smokearray or no data exceeded threshold.")
    exit()

# Download the image
if newestRes.imagecurr: url = newestRes.imagecurr
else: url = newestRes.imagenext
insert_string = username+":"+password+"@"
auth_url = re.sub(r"(//)", r"\1" + insert_string, url)

if newestRes.imageprev: url2 = newestRes.imageprev

#print(auth_url)

while True:
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        # Determine the file name from the URL
        file_name = os.path.basename(auth_url)

        # Save the image to a local file
        with open(file_name, 'wb') as file:
            file.write(response.content)

        print(f"Image downloaded and saved as '{file_name}'.")
        break
    elif response.status_code == 404:
        response = requests.get(url2, auth=(username, password))
        if response.status_code == 200:
            # Determine the file name from the URL
            file_name = os.path.basename(auth_url)

            # Save the image to a local file
            with open(file_name, 'wb') as file:
                file.write(response.content)

            print(f"Image downloaded and saved as '{file_name}'.")
            break

    else:
        print(response.content)
        print(f"Failed to download the file. Status code: {response.status_code}")

# Visualize the data over the image
timestamp, newimage_name = postpro.drawtiles(newestRes, file_name)
fireBool = threshold(newestRes)
metadata = [timestamp, blade, fireBool]
slackbot.sendtoslack(newimage_name, metadata)
