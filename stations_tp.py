from datetime import datetime
import numpy as np
import streamlit as st
import streamlit_folium as stf
import pandas as pd
import folium
import plotly.express as p
from data.computing import get_distances_under_n, get_prices_comparison

from data.data import load_data

st.set_page_config(layout="wide")

merged, infos, infos_100, data = load_data()

st.sidebar.header("Paramètres")

enseignes_choice = infos_100["Enseignes"].unique()

selected_enseigne = "Carrefour"

selected_station = st.sidebar.selectbox("Choisissez une station", infos_100[infos_100["Enseignes"] == selected_enseigne]["ID"])

info_selected_station = merged[merged["id"] == selected_station]["Date_Conv"]
min_date = info_selected_station.min()
max_date = info_selected_station.max()

if min_date and max_date:
    selected_date = st.sidebar.date_input("Date choisie", min_value=min_date, max_value=max_date)
    product = st.sidebar.selectbox("Carburants", ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"])
    radius = st.sidebar.number_input("Périmètre", 1, 50)
    
def details_enseignes(enseignes, date):
    st.write(f"## Détails pour les enseignes")
    st.write(f"### Prix moyens")
    
    per_enseigne = merged[merged["Enseignes"].isin(enseignes)]
    per_enseigne = per_enseigne.drop(["Date", "ID", "id", "Adresse", "Ville", "Latitude", "Longitude", "Type", "Unnamed: 0", "CP"], axis=1)
    per_enseigne = per_enseigne[["Enseignes", "Date_Conv", product]]
    per_enseigne = per_enseigne[per_enseigne[product] != 0]
    per_enseigne = per_enseigne[per_enseigne["Date_Conv"] == date]
    per_enseigne = per_enseigne.drop("Date_Conv", axis=1)
    per_enseigne = per_enseigne.groupby(by="Enseignes").mean().round(2)
    
    col_11, col_12, col_13 = st.columns(3)
    col_14, col_15, col_16 = st.columns(3)
    
    cols = [col_11, col_12, col_13, col_14, col_15, col_16]
    for i, p in enumerate(enseignes):
        cols[i].metric(p, value=str("Pas de service" if per_enseigne.loc[p][product] == 0 else (str(per_enseigne.loc[p][product]) + "€")))
    
details_enseignes(["Carrefour", "Auchan", "E.Leclerc", "TotalEnergies Access", "Intermarché", "Système U"], selected_date)

st.title(f"Station {selected_station} ({selected_enseigne})")
info_s = infos_100[infos_100["ID"] == selected_station]
coords = float(info_s["Latitude"]) / 100_000.0, float(info_s["Longitude"]) / 100_000.0
d_enseigne_w_date = merged[merged["id"] == selected_station]
st.session_state.setdefault("d_enseigne_w_date", d_enseigne_w_date)
d_enseigne = d_enseigne_w_date[d_enseigne_w_date["Date_Conv"] == selected_date]

f_map = folium.Map(coords)
folium.Marker(
    coords, popup=info_s["Adresse"].values.tolist()[0] + ", " + info_s["Ville"].values.tolist()[0], tooltip=info_s["Adresse"].values.tolist()[0] + ", " + info_s["Ville"].values.tolist()[0]
).add_to(f_map)
st.markdown("## Prix")

col_11 = st.columns(1)[0]
if selected_date:
    col_11.metric(product, value=str("Pas de service" if d_enseigne[product].values[0] == 0 else (str(d_enseigne[product].values.tolist()[0]) + "€")))
else:
    st.write("Aucune donnée n'est disponible pour afficher les prix actuels")
    
stations_10 = get_distances_under_n(int(radius), info_s, merged[~(merged["Enseignes"] == selected_enseigne)])

stations_10_data = merged[merged["ID"].astype(str).isin(stations_10[str(selected_station)])]
stations_10_data = stations_10_data[stations_10_data["Date_Conv"] == selected_date]

for k, s in stations_10.items():
    for sta in s:
        
        s_info = infos[infos["ID"] == np.int64(sta)]
    
        folium.Marker(
        (s_info["Latitude"] / 100_000, s_info["Longitude"] / 100_000), popup=s_info["Adresse"].values.tolist()[0] + ", " + s_info["Ville"].values.tolist()[0], tooltip=s_info["Adresse"].values.tolist()[0] + ", " + s_info["Ville"].values.tolist()[0], icon=folium.Icon(color="red")
    ).add_to(f_map)
        
    folium.Circle(
        location=coords,
        radius=int(radius) * 1_000,
        color="black"
    ).add_to(f_map)
stf.st_folium(f_map, zoom=False, width=f_map.width)

station_data = merged[merged["id"] == selected_station]
station_data = station_data[station_data["Date_Conv"] == selected_date]

comparison = stations_10_data[stations_10_data[product] != 0]
diffs = get_prices_comparison(station_data, comparison)

product_diffs = diffs[product].sort_values(ascending=False)

merged_diffs = pd.merge(left=product_diffs, right=infos, left_on=product_diffs.index, right_on="ID")
merged_diffs = merged_diffs.drop(["CP", "Latitude", "Longitude"], axis=1)

st.markdown("### Prix par rapport au voisinage")
if merged_diffs.empty:
    st.write(f"Pas de concurrents sur un rayon de {radius}km")
else:
    st.write(merged_diffs)

st.markdown("## Visualisations")


if merged_diffs.empty:
    st.write(f"Pas de concurrents sur un rayon de {radius}km")
else:
    if selected_date:
        all_p_g = d_enseigne_w_date[["Enseignes", "Adresse", "Date", "Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]]
                
        if(all_p_g[product].median() > 0):
            st.plotly_chart(p.line(title="Prix " + product, data_frame=all_p_g, x="Date", y=product ,labels={"x": "Date", "y": "Prix"}))
    else:
        st.write("Aucune donnée n'est disponible pour visualiser les changements")     