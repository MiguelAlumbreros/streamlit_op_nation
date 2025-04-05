import streamlit as st
# import pandas as pd
# import plotly.express as px
from datetime import datetime
from datetime import timedelta


# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# import io

# make streamlit fit all the window
st.set_page_config(layout="wide")

# st.write("""
# # My first app
# """)

# initialize and store dates in session_state
if "start_day_selection" not in st.session_state:
    # default selection is yesterday
    # st.session_state.start_day_selection  =  (datetime.today() - timedelta(days=1)).date()
    st.session_state.start_day_selection  =  (datetime(2024,6,1)).date()
    
    
if "end_day_selection" not in st.session_state:
    # default selection is yesterday
    st.session_state.end_day_selection  =  st.session_state.start_day_selection
    
if "multi_day_selection" not in st.session_state:
    # default selection is yesterday
    st.session_state.multi_day_selection  =  False 

# st.write(st.session_state)

multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

if not multi_toggle:
    st.session_state.end_day_selection = st.session_state.start_day_selection
start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))


st.write(st.session_state)



# if radio_button == "multi_day":
#     start_date = st.date_input("start date", date)
#     end_date = st.date_input("end date", date)
    
# st.session_state.day_selector = radio_button

# st.write(st.session_state.day_selector)



