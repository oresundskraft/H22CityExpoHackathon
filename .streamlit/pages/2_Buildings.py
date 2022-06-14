import numpy as np
import geopandas as gpd
import plotly.express as px
from haversine import haversine
import streamlit as st
from address import load_address_data

address_df = load_address_data()

@st.experimental_memo(show_spinner=True)
def load_f_s_data():
    f_s_gdf = gpd.read_file("data/fastigheter_och_samfalligheter.gpkg")#CRS: EPSG:3006
    f_s_gdf['Area'] = f_s_gdf['Area'].astype(np.float)
    f_s_gdf['lat'] = f_s_gdf['geometry'].centroid.y
    f_s_gdf['lng'] = f_s_gdf['geometry'].centroid.x
    return f_s_gdf

    
f_s_gdf = load_f_s_data()

streer_name = st.sidebar.text_input('Search addres', '')

filtered_address_df = address_df.copy()
filtered_address_df = filtered_address_df[filtered_address_df['Adress'].str.lower().str.contains(streer_name.lower())]
filtered_address_df = filtered_address_df.reset_index(drop=True)
selected_address = str(st.sidebar.selectbox('Address?',
                                        filtered_address_df['Adress']+'_'+filtered_address_df['Postnummer']+'_'+filtered_address_df['Stad'],
                                        key='building_address_search'))

if 'building_address_search' not in st.session_state:
    st.session_state['building_address_search'] = selected_address


selected_address = selected_address.split('_')
filtered_address = address_df[(address_df['Adress']==selected_address[0]) & (address_df['Postnummer']==selected_address[1])& (address_df['Stad']==selected_address[2])]
filtered_address = filtered_address.head(1)

selected_distance = int(st.sidebar.number_input(f'Distance to selected address? KM', min_value=0.0, max_value=15.0, value=1.0, step=0.5, key='distance'))
if 'distance' not in st.session_state:
    st.session_state['distance'] = selected_distance

filtered_df = f_s_gdf.copy()
def dist(row):
    return haversine((row['lat'],row['lng']),(filtered_address['lat'],filtered_address['lng']))   
filtered_df['distance'] = filtered_df.apply(dist, axis=1)
filtered_df = filtered_df.sort_values(by='distance')


#FILTER 1
detail_types = filtered_df['detaljtyp'].unique()
selected_d_type = st.sidebar.selectbox('detaljtyp', detail_types, key='select_detail_types')
if 'select_detail_types' not in st.session_state:
    st.session_state['select_detail_types'] = selected_d_type

#Apply filters
filtered_df  = filtered_df[filtered_df['detaljtyp']==selected_d_type]
filtered_df  = filtered_df[(filtered_df['distance']<=selected_distance) ]

# fig, ax = plt.subplots()
# filtered_df.head(show_results).plot(ax=ax, color='lightgray')
# filtered_df.head(show_results).plot(column='Area', ax=ax, cmap='viridis')
#ax.set_axis_off()
#st.pyplot(fig)

# plot base map
fig = px.choropleth_mapbox(filtered_df,
                   geojson=filtered_df.geometry,
                   locations=filtered_df.index,
                   color="Area",
                   height=600,width=600,
                   mapbox_style="carto-positron",
                   opacity=0.5,
                   zoom=11, center = {"lat": float(filtered_address['lat']), "lon": float(filtered_address['lng'])},)
#fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig)


    


