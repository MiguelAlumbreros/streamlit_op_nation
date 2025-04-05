import streamlit as st
from st_clickable_images import clickable_images
from streamlit_extras.switch_page_button import switch_page

with st.sidebar:
    # start_date = st.date_input("start date", default_start_date)
    # end_date = st.date_input("end date", default_end_date)
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))



clicked = clickable_images(
    [
        "https://media.giphy.com/media/MEeF0LoWyiaJnqFXol/giphy.gif?w=1000",
        "https://media.giphy.com/media/s4M6Ez9lbsOF5x3rXA/giphy.gif?w=100",
        "https://images.unsplash.com/photo-1582550945154-66ea8fff25e1?w=700",
        "https://images.unsplash.com/photo-1591797442444-039f23ddcc14?w=700",
        "https://images.unsplash.com/photo-1518727818782-ed5341dbd476?w=700",
    ],
    titles=[f"Image #{str(i)}" for i in range(5)],
    div_style={"display": "block", "justify-content": "center", "flex-wrap": "wrap"},
    img_style={"margin": "6px", "height": "200px", "width": "200px"},
)

st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")

if clicked == 0:
    switch_page('kpi')