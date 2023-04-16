import os
from itertools import permutations

import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.spatial import distance_matrix


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def avg_distance(df, nomLine, sens):
    # Filtrer les lignes en fonction de la condition nomcourtligne == 'C1' et sens == 0
    filtered_df = df[df["nomcourtligne"] == nomLine]
    filtered_df = filtered_df[filtered_df["sens"] == sens]

    # Extraire les coordonnées et les diviser en latitude et longitude
    filtered_df['latitude'] = filtered_df['coordonnees'].apply(
        lambda x: float(x.replace("[", "").split(",")[0].strip('[]')))
    filtered_df['longitude'] = filtered_df['coordonnees'].apply(
        lambda x: float(x.replace("]", "").split(",")[1].strip('[]')))

    # Calculate pairwise distances
    coords = filtered_df[['latitude', 'longitude']].to_numpy()
    dist_matrix = distance_matrix(coords, coords)

    # Calculate total distance for each permutation of buses
    total_distances = [sum(dist_matrix[i, j] for i, j in zip(perm, perm[1:]))
                       for perm in permutations(range(len(coords)))]

    if len(coords) == 0:
        return -1
    # Find the minimum total distance and calculate the average distance
    if total_distances:
        min_total_distance = min(total_distances)
        avg_distance = min_total_distance / len(coords)
    else:
        avg_distance = None

    return avg_distance * 1000


def avg_time_diff(df, nomLine, sens):
    # Filtrer les lignes en fonction de la condition nomcourtligne == 'C1' et sens == 0
    filtered_df = df[df["nomcourtligne"] == nomLine]
    filtered_df = filtered_df[filtered_df["sens"] == sens]

    # Extract the "ecartsecondes" column and convert it to a list
    time_diffs = filtered_df['ecartsecondes'].tolist()

    # Calculate the average time difference
    if time_diffs:
        avg_time_diff = sum(time_diffs) / len(time_diffs)
    else:
        avg_time_diff = None
    return avg_time_diff


def bus_count(df, nomLine, sens):
    # Filtrer les lignes en fonction de la condition nomcourtligne == 'C1' et sens == 0
    filtered_df = df[df["nomcourtligne"] == nomLine]
    filtered_df = filtered_df[filtered_df["sens"] == sens]

    # Obtenir le nombre de bus
    bus_count = len(filtered_df)
    return bus_count


def lenOfLine(nomLine, sens):
    with open('data_fix/tco-bus-topologie-parcours-td.csv', 'r') as f:
        lines = f.readlines()
        lines = [line.strip().replace('"', '') for line in lines]
        lines = [line.split(';') for line in lines]
    # convert the list to a dataframe with line 0 the header
    dfTopo = pd.DataFrame(lines[1:], columns=lines[0])
    # get the value the column Longueur if Ligne (nom court) == nomLine and Code du sens == sens
    tmp = dfTopo.loc[(dfTopo['Ligne (nom court)'] == nomLine.replace("'", "").replace(" ", "")) & (
            dfTopo['Code du sens'] == str(sens)) & (
                             dfTopo['Type'] == 'Principal'), 'Longueur'].iloc[0]
    return float(tmp)


def getDay(df):
    # get date from df and convert format YYYY-MM-DD into format YYYY-MM-DD
    D = pd.to_datetime(df['date']).dt.day_name().iloc[0]
    D = D.replace('Monday', '0').replace('Tuesday', '0').replace('Wednesday', '0').replace('Thursday',
                                                                                           '0').replace(
        'Friday', '0').replace('Saturday', '1').replace('Sunday', '2')
    return int(D)


def getMaxFreq(df, nomLine, level):
    with open('data_fix/mkt-frequentation-niveau-freq-max-ligne.csv', 'r') as f:
        lines = f.readlines()
        lines = [line.strip().replace('"', '') for line in lines]
        lines = [line.split(';') for line in lines]
    # convert the list to a dataframe with line 0 the header
    dfFreq = pd.DataFrame(lines[1:], columns=lines[0])

    # get houre from df and convert format HH:MM:SS into format HH:MM and round to the nearest 30 minutes
    H = pd.to_datetime(df['heure']).dt.round('30min').dt.time.iloc[0]
    H = str(H).replace(":00:00", ":00").replace(":30:00", ":30")

    # get date from df and convert format YYYY-MM-DD into format lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche
    D = pd.to_datetime(df['date']).dt.day_name().iloc[0]
    # convert to french
    D = D.replace('Monday', 'Lundi-vendredi').replace('Tuesday', 'Lundi-vendredi').replace(
        'Wednesday', 'Lundi-vendredi').replace('Thursday', 'Lundi-vendredi').replace('Friday',
                                                                                     'Lundi-vendredi').replace(
        'Saturday', 'Samedi').replace('Sunday', 'Dimanche')

    # get the value the column Niveau_fréquentation if Ligne == nomLine and Tranche_horaire == H and Jour == D
    selected_rows = dfFreq.loc[
        (dfFreq['Ligne'] == nomLine.replace("'", "").replace(" ", "")) & (dfFreq['Tranche_horaire'] == str(H)) & (
                dfFreq['Jour_semaine'] == D), 'Niveau_frequentation']

    if not selected_rows.empty:
        tmp = selected_rows.iloc[0]
    else:
        tmp = -1  # or any other default value you want to assign when no rows are found

    if tmp == '' or tmp == -1:
        return -1

    if level == float(tmp):
        return 1
    else:
        return 0


# Chemin du dossier contenant les fichiers CSV
data_folder = "../dataCopy"

nomLine = "C1"
sens = 0

dfTotal = pd.DataFrame(
    columns=['avg_distance', 'avg_time_diff', 'bus_count', 'length', 'day', 'maxFreqL', 'maxFreqM', 'maxFreqH'])

# Parcourir tous les fichiers du dossier
# Convert the data type to float32
i = 0
for file in os.listdir(data_folder):
    # Vérifier si le fichier est un fichier CSV
    if file.endswith(".csv"):
        # Construire le chemin complet du fichier
        file_path = os.path.join(data_folder, file)
        i += 1
        # Lire le fichier CSV et le convertir en dataframe
        try:
            df = pd.read_csv(file_path, sep=';')
        except pd.errors.EmptyDataError:
            print(f"Skipping empty or invalid file: {file_path}")
            continue

        # check if nomLine are in the dataframe sinon passer au fichier suivant
        if df.empty:
            continue

        if not nomLine in df['nomcourtligne'].astype(str).unique():
            continue

        # Create a new dataframe with the average distance difference, average time difference, and the number of buses, the length of the line , the max frequency
        data = {'avg_distance': [avg_distance(df, nomLine, sens)],
                'avg_time_diff': [avg_time_diff(df, nomLine, sens)],
                'bus_count': [bus_count(df, nomLine, sens)], 'length': [lenOfLine(nomLine, sens)],
                'day': [getDay(df)],
                'maxFreqL': [getMaxFreq(df, nomLine, 1)],
                'maxFreqM': [getMaxFreq(df, nomLine, 2)],
                'maxFreqH': [getMaxFreq(df, nomLine, 3)]}
        if data['maxFreqL'] == [-1] or data['maxFreqM'] == [-1] or data['maxFreqH'] == [-1]:
            continue

        summary_df = pd.DataFrame(data, columns=['avg_distance', 'avg_time_diff', 'bus_count', 'length',
                                                 'day', 'maxFreqL', 'maxFreqM', 'maxFreqH'])

        # add the new dataframe to the total dataframe with concat
        dfTotal = pd.concat([dfTotal, summary_df], ignore_index=True)

        if not i % 1:
            print(i)

print(i)
dfTotal = dfTotal.astype(np.float32)

dfTotal = dfTotal.dropna()

# enregistrer le dataframe dans un fichier csv
dfTotal.to_csv('DataIA/data_' + nomLine + '_' + sens + '.csv', index=False)
