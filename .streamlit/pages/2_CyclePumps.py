import os
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from address import load_address_data
from util import geodesic_point_buffer

address_df = load_address_data()

if os.name == 'nt':
    file_path_prefix = '.'
else:
    file_path_prefix = os.getcwd() + '/.streamlit'
    
@st.experimental_memo(show_spinner=True)
def load_transport_data(): 
    cykelpumpar_gdf = gpd.read_file(file_path_prefix+"/data/transport/cykelpumpar.gpkg")#CRS: EPSG:3006 #  
    return cykelpumpar_gdf

    
cykelpumpar_gdf = load_transport_data()

filtered_df = cykelpumpar_gdf.copy()
#st.write(filtered_df)
filtered_df['lat'] = filtered_df['geometry'].y
filtered_df['lng'] = filtered_df['geometry'].x  

if len(filtered_df)>0:    
    fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lng", zoom=11,
                            height=600,width=600,
                            hover_name='Beskrivning',color='Pumptyp')
    fig.update_layout(mapbox_style="open-street-map")

    fig.update_traces(marker={'size': 15,'opacity':0.8})
    
    st.plotly_chart(fig)

else:
    "# No results to display!"
    


