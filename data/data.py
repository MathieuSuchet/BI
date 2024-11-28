import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_data():
    loading = st.progress(0, "Chargement des données")
    merged = pd.read_csv("BI app/Infos_Prix_2024.csv")
    merged["Date_Conv"] = merged["Date"].apply(lambda d: datetime.strptime(d, "%Y-%m-%d").date())
    
    loading.progress(1.0 / 4.0, "Chargement des données")

    infos = pd.read_csv("BI app/Infos_Stations.csv")
    loading.progress(2.0 / 4.0, "Chargement des données")

    infos_100 = pd.read_csv("BI app/Infos_Stations_100.csv")
    loading.progress(3.0 / 4.0, "Chargement des données")

    data = pd.read_csv("BI app/Prix_2024.csv")
    loading.progress(4.0 / 4.0, "Chargement des données")
    loading.empty()
    
    return merged, infos, infos_100, data