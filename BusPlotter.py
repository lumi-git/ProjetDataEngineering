import pandas as pd
import os
from generator.utils import timit
from generator.utils import printProgress
from generator.utils import printProgressWithEstimation
import imageio
import plotly.express as px
import time

FILES_TO_LOAD = -1


@timit
def plotMap(time_):
    Folder = "DataCopy"
    locations = []

    total_processing_time = 0
    avg_time_per_file = 0

    if FILES_TO_LOAD == -1:
        FileList = os.listdir(Folder)
    else:
        FileList = os.listdir(Folder)[:FILES_TO_LOAD]
    size = len(FileList)

    print(f"1/ loading {size} files. (may take time) ...")

    path = "VideoOutput/"

    with imageio.get_writer(path + 'MapVideo_30FPS_' + str(size) + 'files.mp4', fps=30) as video_writer:
        try:
            i = 0
            for file in FileList:
                start_time = time.time()

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

                i += 1
                total_processing_time += (time.time() - start_time)
                avg_time_per_file = total_processing_time / i
                estimated_time = avg_time_per_file * size
                if (i % 100 == 0):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    printProgressWithEstimation(i, size, time_, estimated_time)

        except(Exception) as e:
            print("Error at file" + file)
            print(e)
            print(file)
            exit()

        if locations:
            i = 1
            len_ = len(locations)
            for loc in locations:
                start_time = time.time()
                date_time = loc['date'][0] + " " + loc['heure'][0]
                fig = px.scatter_mapbox(loc, lat="latitude", lon="longitude", zoom=10, height=600, width=800,
                                        center=dict(lat=48.11269100094845, lon=-1.6766415476680276),
                                        title=date_time, color="ecartsecondes",
                                        color_continuous_scale="Viridis",
                                        range_color=[-500, 500])  # Set the range for "ecartsecondes"

                fig.update_layout(mapbox_style="open-street-map")
                img_bytes = fig.to_image(format="png")

                video_writer.append_data(imageio.v2.imread(img_bytes))

                os.system('cls' if os.name == 'nt' else 'clear')
                total_processing_time += (time.time() - start_time)
                avg_time_per_file = total_processing_time / i
                estimated_time = avg_time_per_file * size
                printProgressWithEstimation(i, size, time_, estimated_time)
                i += 1


plotMap()