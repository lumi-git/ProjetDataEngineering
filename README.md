# ProjetDataEngineering



## Pre-setup

To be able to run the project you need to scrap the data from Star API.
For this project we run the following script to get the data from the API on a NAS for 2 months.

```py
import os
import datetime
from time import sleep
from requests import request

# send request the API and get the response
def get_response():
    isNotConnected = True
    while isNotConnected:
        try:
            response = request("GET","https://data.explore.star.fr/api/records/1.0/search/?dataset=tco-bus-vehicules-position-tr&q=&rows=1000&facet=numerobuskr&facet=numerobus&facet=nomcourtligne")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)


while True:
    # open the create file with date and time on name
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open('Data/bus_{}.txt'.format(time), 'w') as f:
        # get the response
        response = get_response()
        # write the response in the file
        for record in response['records']:
            f.write(str(record['fields']) + '\n')

    # count the number of file in the folder Data
    number_of_file = len([name for name in os.listdir('Data/')])
    print(number_of_file, time)
    sleep(29) # sleep 29 secondes to get the data every 30 secondes
```

At the end of the scrapping we have 14.1 Go.

Link to the data we scrap : https://drive.google.com/file/d/1lznKlHMYa_clsgkexL7PG2Wiiq-gShZS/view?usp=sharing


## Setup

Remove the indicative file from the folders and copy the data to the Data folder.


## Pre-analysis

Look at the data and the pre-analysis in the [Date.ipynb](./Date.ipynb) notebook.

or

Run the [Date.ipynb](./Date.ipynb) notebook to see a preview of the data and pre-analysis.


### Data cleaning
run the following command to create a copy of the data in the Data folder (create a DataCopy folder).

```bash
python3 ./generator/RawToCSV.py
```

### Data analysis video

run  the following command to create a video of the data.
```bash
python3 ./BusPlotter.py
```
You can see the [video](https://drive.google.com/file/d/142b3_2_urGZfN7PI0_pnWJYAq_xexvOO/view?usp=sharing) we made with the data.

## Heatmap

![](./MapImage.png)
(open the image in a new tab to see it in full size and zoom in)
Look at the code in the [HeatMap.ipynb](./HeatMap.ipynb) notebook.
Run the [HeatMap.ipynb](./HeatMap.ipynb) notebook to generate the heatmap.
