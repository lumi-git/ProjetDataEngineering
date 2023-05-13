import threading

import pandas as pd
import os
from generator.utils import timit
from generator.utils import printProgress
import plotly.express as px
import math

Folder = "DataCopy"


class worker(threading.Thread):
    progress = 0
    lock = threading.Lock()

    def __init__(self, filesNames=[], max=0):
        super().__init__()
        self.result = None
        self.fileNames = filesNames
        self.max = max

    def run(self):
        for file in self.fileNames:
            worker.lock.acquire()
            worker.progress += 1
            worker.lock.release()
            with open(Folder + "/" + file, 'r') as f:
                lines = f.readlines()
                if len(lines) == 0:
                    continue

            # pre-processing
            df = pd.read_csv(Folder + "/" + file, sep=";")
            if not df.empty:
                df[['latitude', 'longitude']] = df['coordonnees'].apply(
                    lambda x: pd.Series(x.strip('[]').replace("[", "").replace("]", "").split(','))).astype(float)
                self.result = df
            else:
                # add a row with the date and time on df
                date = file.split("_")[1]
                heure = file.split("_")[2].replace("-", ":").replace(".csv", "")
                new_row = {'sens': 0, 'numerobus': 0, 'numerobuskr': 0, 'voiturekr': 0, 'idbus': 0, 'idligne': 0,
                           'etat': 0, 'destination': 0, 'nomcourtligne': 0, 'coordonnees': 0, 'ecartsecondes': 0,
                           'date': date, 'heure': heure, 'latitude': 0, 'longitude': 0}
                df = pd.DataFrame([new_row])
                self.result = df
            printProgress(worker.progress + 1, self.max)


FILES_TO_LOAD = -1  # 5000
POINTSIZE = 2


def round_coordinates(coord, decimals=4):
    return round(coord, decimals)


@timit
def plotMap(time_):
    Folder = "DataCopy"
    locations = []

    if FILES_TO_LOAD == -1:
        FileList = os.listdir(Folder)
    else:
        FileList = os.listdir(Folder)[:FILES_TO_LOAD]
    size = len(FileList)

    # separate the files in n groups to be loaded in parallel

    groups = []

    print(f"1/ loading {size} files. (may take time) ...")

    n = 15

    threads = []
    for i in range(n):
        t = worker(FileList[i::n], size)
        t.start()
        threads.append(t)
        t.join()
        print(f"thread {FileList[i::n]} finished")

    for t in threads:
        locations.append(t.result)

    """
    for idx, file in enumerate(FileList):
        # verification if the file is empty
        with open(Folder + "/" + file, 'r') as f:
            lines = f.readlines()
            if len(lines) == 0:
                continue

        # pre-processing
        df = pd.read_csv(Folder + "/" + file, sep=";")
        if not df.empty:
            df[['latitude', 'longitude']] = df['coordonnees'].apply(
                lambda x: pd.Series(x.strip('[]').replace("[", "").replace("]", "").split(','))).astype(float)
            locations.append(df)
        else:
            # add a row with the date and time on df
            date = file.split("_")[1]
            heure = file.split("_")[2].replace("-", ":").replace(".csv", "")
            new_row = {'sens': 0, 'numerobus': 0, 'numerobuskr': 0, 'voiturekr': 0, 'idbus': 0, 'idligne': 0,
                       'etat': 0, 'destination': 0, 'nomcourtligne': 0, 'coordonnees': 0, 'ecartsecondes': 0,
                       'date': date, 'heure': heure, 'latitude': 0, 'longitude': 0}
            df = pd.DataFrame([new_row])
            locations.append(df)

        # Update the progress bar
        printProgress(idx + 1, size)
    """

    # Concatenate all DataFrames in the locations list
    all_locations = pd.concat(locations)

    # Round coordinates and group by rounded coordinates
    all_locations['rounded_lat'] = all_locations['latitude'].apply(round_coordinates)
    all_locations['rounded_lon'] = all_locations['longitude'].apply(round_coordinates)
    all_locations['ecartsecondes'] = pd.to_numeric(all_locations['ecartsecondes'], errors='coerce')
    all_locations['ecartsecondes'] = all_locations['ecartsecondes'].fillna(0)
    grouped_locations = all_locations.groupby(['rounded_lat', 'rounded_lon']).mean(numeric_only=True).reset_index()

    grouped_locations['point_size'] = POINTSIZE

    print("\nGenerating map image...")

    # Create the scatter mapbox plot
    fig = px.scatter_mapbox(grouped_locations, lat="rounded_lat", lon="rounded_lon", zoom=15, height=2000, width=2000,
                            center=dict(lat=48.11269100094845, lon=-1.6766415476680276), title=f"Bus locations",
                            color="ecartsecondes", color_continuous_scale="Viridis", range_color=[-500, 500],
                            opacity=0.5, size="point_size", size_max=POINTSIZE)

    fig.update_layout(mapbox_style="open-street-map")
    fig.write_image("MapImage.png")

    print("\nMap image saved as 'MapImage.png'")


plotMap()
