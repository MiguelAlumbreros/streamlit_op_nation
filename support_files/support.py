# import streamlit as st
# from streamlit_extras.switch_page_button import switch_page 
# from st_click_detector import click_detector
 
# # import Plotting_Demo
 
# content = """
# <div class="row">
#    <a href='#' id='Image 1'><img width="200" height="150" src='https://media.giphy.com/media/PALn4w1gAd0n7x77i7/giphy.gif?w=400'></a>
# <div class="row">
#    <a href='#' id='Image 2'><img width="200" height="150"  src='https://media.giphy.com/media/mGvgMFgKrP2U19qMdS/giphy.gif?w=400'></a>

# <div class="column">

#    """
# clicked = click_detector(content)
 
# st.markdown(f"**{clicked} clicked**" if clicked != "" else "**No click**")
 
# if clicked == "Image 2":
#    switch_page("main")