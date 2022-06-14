
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine, Unit
import streamlit as st
from address import load_address_data

@st.experimental_memo(show_spinner=True)
def load_play_data():
    play_gdf = gpd.read_file("data/lekplatser.gpkg")#CRS: EPSG:3006

    return play_gdf
    
play_gdf = load_play_data()
address_df = load_address_data()

filtered_df = play_gdf.copy()

filtered_df['lat'] = filtered_df['geometry'].y
filtered_df['lng'] = filtered_df['geometry'].x  
filtered_address = None

filtered_df.fillna('missing', inplace=True)


address_search = st.sidebar.checkbox('Advanced search', value=False, key='activities_address_search')
if address_search:
    streer_name = st.sidebar.text_input('Search addres', '')
    
    filtered_address_df = address_df.copy()
  
    filtered_address_df = filtered_address_df[filtered_address_df['Adress'].str.lower().str.contains(streer_name.lower())]
    filtered_address_df = filtered_address_df.reset_index(drop=True)

    selected_address = str(st.sidebar.selectbox('Address?',
        filtered_address_df['Adress']+'_'+filtered_address_df['Postnummer']+'_'+filtered_address_df['Stad'],key='address'))

    if 'address' not in st.session_state:
        st.session_state['address'] = selected_address    
        
    selected_address_split = selected_address.split('_')
    if len(selected_address_split) > 1:
        filtered_address = filtered_address_df[(filtered_address_df['Adress']==selected_address_split[0]) & 
                                            (filtered_address_df['Postnummer']==selected_address_split[1]) &
                                            (filtered_address_df['Stad']==selected_address_split[2])]
        filtered_address = filtered_address.head(1)
    else:
        filtered_address = address_df.head(1)
        

    def dist(row):
        return haversine((row['lat'],row['lng']),(filtered_address['lat'],filtered_address['lng']))   
    filtered_df['distance'] = filtered_df.apply(dist, axis=1)
    filtered_df = filtered_df.sort_values(by='distance')

    selected_distance = int(st.sidebar.number_input(f'Distance to selected address? KM ', min_value=0.0, max_value=15.0, value=2.0, step=0.5, key='distance'))
    if 'distance' not in st.session_state:
        st.session_state['distance'] = selected_distance
    filtered_df  = filtered_df[(filtered_df['distance']<=selected_distance) ]

    #FILTER 1
    categories = filtered_df['Lekplatskategori'].unique()
    multi_selected_category = st.sidebar.multiselect('Lekplatskategori', categories, default=['narlekplats'], key='multi_select_category')

    if 'multi_select_category' not in st.session_state:
        st.session_state['multi_select_category'] = multi_selected_category    
    filtered_df  = filtered_df[(filtered_df['Lekplatskategori'].isin(multi_selected_category)) ]


# plot base map
# fig = px.choropleth_mapbox(filtered_df,
#                    geojson=filtered_df.geometry,
#                    locations=filtered_df.index,
#                    color="Agartyp",
#                    height=800,width=800,
#                    mapbox_style="carto-positron",
#                    opacity=0.5,
#                    zoom=12, center = {"lat": float(filtered_address['lat']), "lon": float(filtered_address['lng'])},)
#fig.update_geos(fitbounds="locations", visible=False)


fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lng", zoom=11,height=800,width=1024,
                        hover_name='Namn',color='Lekplatskategori')
fig.update_layout(mapbox_style="open-street-map")
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(marker={'size': 15,'opacity':0.8})
if address_search:
    fig.add_trace(go.Scattermapbox(
        #mode = "markers",
        lon = [float(filtered_address['lng']) ],
        lat = [float(filtered_address['lat']) ],
        marker = {'size': 15}))

st.plotly_chart(fig)

if address_search:
    st.write(filtered_df)


    


