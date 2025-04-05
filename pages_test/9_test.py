import streamlit as st
from streamlit_imagegrid import streamlit_imagegrid
import requests
from PIL import Image
from io import BytesIO

st.title('Image grid test')
zoom_val = st.sidebar.slider('Zoom',40,240)

urls = [ { "width": 1000, "height": 500, "src": "https://as2.ftcdn.net/jpg/02/25/53/52/1000_F_225535263_n14yO9cXk18X90qQYxBf5Vcf00uOtAhW.jpg" },
        { "width": 1000, "height": 500, "src": "https://as2.ftcdn.net/jpg/02/81/07/83/1000_F_281078312_PcISs3yKL9r70nCqvDkgOR17UBGIw97C.jpg" },
        { "width": 1000, "height": 500, "src": "https://as2.ftcdn.net/jpg/02/96/35/64/1000_F_296356423_f6IEidPVRWzaqj2MJQ2VLJJTYGRAtY4P.jpg" } ]

return_value = streamlit_imagegrid(urls=urls,zoom=zoom_val,height=1000)


if return_value is not None:
    response = requests.get(return_value)
    st.sidebar.markdown('<img src={} width=240px></img>'.format(return_value),unsafe_allow_html=True)
    print(response)
    
# st.image(filteredImages, width=150, caption=caption)

# for image in filteredImages:
#    r = requests.get(image)
#    img = Image.open(BytesIO(r.content))
#    resizedImg = img.resize((225, 325), Image.ANTIALIAS)
#    resizedImages.append(resizedImg)

# a 2x2 grid the long way
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.write('Caption for first chart')
    with col2:
        st.image('https://as2.ftcdn.net/jpg/02/25/53/52/1000_F_225535263_n14yO9cXk18X90qQYxBf5Vcf00uOtAhW.jpg')
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.write('Caption for second chart')
    with col2:
        st.line_chart((1,0), height=100)
