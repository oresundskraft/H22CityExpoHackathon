import geopandas as gpd
import streamlit as st

@st.experimental_memo(show_spinner=True)
def load_address_data():
    address_df = gpd.read_file("data/adresser.gpkg")#CRS: EPSG:3006
    address_df['lat'] = address_df['geometry'].y
    address_df['lng'] = address_df['geometry'].x    
    return address_df