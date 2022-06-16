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
    parkeringsautomater_gdf = gpd.read_file(file_path_prefix+"/data/transport/parkeringsautomater.gpkg")#CRS: EPSG:3006    
    return parkeringsautomater_gdf

    
parking_terminals_gdf = load_transport_data()

filtered_df = parking_terminals_gdf.copy()
#st.write(filtered_df)
filtered_df['lat'] = filtered_df['geometry'].y
filtered_df['lng'] = filtered_df['geometry'].x  

active_parking_terminal = st.sidebar.checkbox(f'Only Active Parking Terminals', value=False, key='parking_terminal_active')

if active_parking_terminal:
    filtered_df  = filtered_df[(filtered_df['Status']=='aktiv') ]
    

address_search = st.sidebar.checkbox('Advanced search', value=False, key='parking_address_search')
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
    
    #Avgbeltid_vard_helg
    # selected_weekday_time_range = str(st.sidebar.selectbox('Weekdays',
    #     filtered_df['Avgbeltid_vardag'].unique(), key='selection_weekday'))

    # if 'selection_weekday' not in st.session_state:
    #     st.session_state['selection_weekday'] = selected_weekday_time_range    
    # filtered_df  = filtered_df[(filtered_df['Avgbeltid_vardag']==selected_distance) ]
    
    
    
    
if len(filtered_df)>0:    
    fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lng", zoom=11,
                            height=600,width=600,
                            hover_name='Namn',color='Taxa_avgbeltid')
    fig.update_layout(mapbox_style="open-street-map")

    fig.update_traces(marker={'size': 15,'opacity':0.8})
    if address_search:
        coords=geodesic_point_buffer(float(filtered_address['lat']), float(filtered_address['lng']), selected_distance)
        layers=dict(type = 'FeatureCollection',
                            features=[{
                                "id":"7", 
                                    "type": "Feature",
                                    "properties":{},
                                    "geometry": {"type": "LineString",
                                                "coordinates": coords
                                                }
                                    }]
                            )
        fig.update_layout(
                mapbox={
                    "layers": [
                        {"source": layers, "color": "PaleTurquoise", "type": "fill", "opacity":.3},
                        {"source": layers, "color": "black", "type": "line", "opacity":.6}

                    ]
                }
            )          
        fig.add_trace(go.Scattermapbox(
            name = filtered_address['Adress'].values[0],
            lon = [float(filtered_address['lng']) ],
            lat = [float(filtered_address['lat']) ],
            hovertext=filtered_address['Adress'].values[0],  
            hoverinfo='text',                            
            marker=dict(size=20, color='black'))         
                    )

    st.plotly_chart(fig)

else:
    "# No results to display!"
    


