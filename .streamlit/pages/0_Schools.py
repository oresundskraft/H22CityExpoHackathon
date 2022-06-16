import os
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from address import load_address_data

address_df = load_address_data()

if os.name == 'nt':
    file_path_prefix = '.'
else:
    file_path_prefix = os.getcwd() + '/.streamlit'
    
@st.experimental_memo(show_spinner=True)
def load_schools_data():
    f_school_gdf = gpd.read_file(file_path_prefix+"/data/schools/forskola.gpkg")#CRS: EPSG:3006
    gr_school_gdf = gpd.read_file(file_path_prefix+"/data/schools/grundskola.gpkg")#CRS: EPSG:3006
    gy_school_gdf = gpd.read_file(file_path_prefix+"/data/schools/gymnasieskola.gpkg")#CRS: EPSG:3006
    s_school_gdf = gpd.read_file(file_path_prefix+"/data/schools/sarskola.gpkg")#CRS: EPSG:3006
    return pd.concat([ f_school_gdf,gr_school_gdf,gy_school_gdf,s_school_gdf])
    
schools_gdf = load_schools_data()
filtered_df = schools_gdf.copy()
filtered_df['lat'] = filtered_df['geometry'].y
filtered_df['lng'] = filtered_df['geometry'].x  

filtered_address = None

address_search = st.sidebar.checkbox('Advanced search', value=False, key='school_address_search')
if address_search:
    streer_name = st.sidebar.text_input('Search addres', '', key="input_street_name")
    
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
    huvudmans = filtered_df['huvudman'].unique()
    multi_selected_huvudman = st.sidebar.multiselect('huvudman', huvudmans, default=['Fristående','Helsingborgs stads skolor'], key='multi_select_huvudman')

    if 'multi_select_huvudman' not in st.session_state:
        st.session_state['multi_select_huvudman'] = multi_selected_huvudman    
    filtered_df  = filtered_df[(filtered_df['huvudman'].isin(multi_selected_huvudman)) ]


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


fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lng", zoom=11,
                        height=600,width=600,
                        hover_name='namn',color='skoltyp')
fig.update_layout(mapbox_style="open-street-map")
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(marker={'size': 15,'opacity':0.8})


if address_search:
    fig.add_trace(go.Scattermapbox(
        name = filtered_address['Adress'].values[0],
        lon = [float(filtered_address['lng']) ],
        lat = [float(filtered_address['lat']) ],
        hovertext=filtered_address['Adress'].values[0],  
        hoverinfo='text',                            
        marker=dict(size=20, color='black'))         
                  )

st.plotly_chart(fig)

if address_search:
    st.write(filtered_df)


    


