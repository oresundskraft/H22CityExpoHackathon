import geopandas as gpd
import streamlit as st
import os

if os.name == 'nt':
    file_path_prefix = '.'
else:
    file_path_prefix = os.getcwd() + '/.streamlit'
    
@st.experimental_memo(show_spinner=True)
def load_address_data():
    address_df = gpd.read_file(file_path_prefix+"/data/adresser.gpkg")#CRS: EPSG:3006
    address_df['lat'] = address_df['geometry'].y
    address_df['lng'] = address_df['geometry'].x    
    return address_df