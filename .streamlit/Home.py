import streamlit as st
from util import file_path

st.set_page_config(
    page_title="H22 Hackathon",
    page_icon="ð",
)

st.sidebar.success("App Version: 1.0,")
st.sidebar.success("ÃKAB Data Science Team. ")

"# H22 City Expo Hackathon! ð"

"## Powered by Helsingborg City Open Data"
"https://helsingborg.io/dataportal/"

'For best experience, open this App on Large Screens'

"## Code"
"https://github.com/oresundskraft/H22CityExpoHackathon.git"
   
st.image(file_path() + "/images/helsingborg.PNG")

