import pandas as pd 
import math
import streamlit as st

def haversine(lat1, lon1, lat2, lon2):
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Rayon moyen de la Terre en kilomètres
    R = 6371.0
    # Différences de coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon /
    2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Distance en kilomètres
    distance = R * c
    return distance

@st.cache_data
def get_distances_under_n(distance: int, station, all_stations):

    station["ID"] = station["ID"].apply(str)
    station["Latitude"] = station["Latitude"].apply(float)/100000
    station["Longitude"] = station["Longitude"].apply(float)/100000
    D1 = {station.loc[id,"ID"] : (station.loc[id,"Latitude"],station.loc[id,"Longitude"]) for id in station.index}

    all_stations["ID"] = all_stations["ID"].apply(str)
    all_stations["Latitude"] = all_stations["Latitude"].apply(float)/100000
    all_stations["Longitude"] = all_stations["Longitude"].apply(float)/100000
    D2 = {all_stations.loc[id,"ID"] : (all_stations.loc[id,"Latitude"],all_stations.loc[id,"Longitude"]) for id in all_stations.index}

    D = dict()
    def list_concurrents(id):
        L_conc = list()
        for x in D2:
            d = haversine(D1[id][0], D1[id][1], D2[x][0], D2[x][1])
            #d = great_circle(D2[id], D1[x]).kilometers
            if d <= distance:
                L_conc.append(x)
        return L_conc

    D = {id : list_concurrents(id) for id in D1}
    
    return D

def get_prices_comparison(station, all_stations):
    df = pd.DataFrame(all_stations)[["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]]
    sta = pd.DataFrame(station)[["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]]
    
    diffs = df - sta.values.squeeze()
    diffs = diffs.set_index(all_stations["ID"])
    return diffs