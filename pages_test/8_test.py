# import streamlit as st
# from streamlit_extras.switch_page_button import switch_page
 
# want_to_contribute = st.button("I want to contribute!")
# if want_to_contribute:
#   switch_page("Contribute")
 
 
import streamlit as st
from st_click_detector import click_detector
from streamlit_extras.switch_page_button import switch_page
 
# import Plotting_Demo
 
content = """<p><a href='#' id='Link 1'>First link</a></p>
   <p><a href='#' id='Link 2'>Second link</a></p>
   <a href='#' id='Image 1'><img width='40%' src='https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/giphy.gif?w=400'></a>
   <a href='#' id='Image 2'><img width='40%' src='https://media.giphy.com/media/mGvgMFgKrP2U19qMdS/giphy.gif?w=400'></a>
   """
clicked = click_detector(content)
 
st.markdown(f"**{clicked} clicked**" if clicked != "" else "**No click**")
 
if clicked == "Image 2":
   switch_page("kpi")