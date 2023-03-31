from multiprocessing import Pool

import pandas as pd
import os
from utils import timit
from utils import printProgress
import imageio
import plotly.express as px
import time

FILES_TO_LOAD = 1000

@timit
def plotMap(time_) :
    Folder = "DataCopy"
    locations = []

    FileList = os.listdir(Folder)[:FILES_TO_LOAD]
    size = len(FileList)

    print(f"1/ loading {size} files. (may take time) ...")


    with imageio.get_writer('MapVideo_30FPS_10files.mp4', fps=30) as video_writer:
        try :
            i = 0
            for file in FileList :

                df = pd.read_csv(Folder+"/" + file)
                if not df.empty :
                    df[['latitude', 'longitude']] = df['coordonnees'].apply(lambda x: pd.Series(x.strip('[]').replace("[", "").replace("]", "").split(';'))).astype(float)
                    locations.append(df)
                i+=1
                if (i%100 == 0):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    printProgress(i, size,time_)

        except( Exception ) as e :
            print("Error at file" + file )
            print(e)

        if locations:
            i=0
            len_ = len(locations)
            st = time.time()
            for loc in locations :

                fig = px.scatter_mapbox(loc, lat="latitude", lon="longitude", zoom=10, height=600, width=800,center=dict(lat=48.11269100094845, lon=-1.6766415476680276))
                fig.update_layout(mapbox_style="open-street-map")
                img_bytes = fig.to_image(format="png")

                video_writer.append_data(imageio.v2.imread(img_bytes))
                os.system('cls' if os.name == 'nt' else 'clear')
                printProgress(i, len_,st)
                i+=1


plotMap()