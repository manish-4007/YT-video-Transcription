import streamlit as st 

import glob
import os 
with open("README.md", 'r',encoding="utf8") as f:
    readme_line = f.read()
    
st.markdown(readme_line,unsafe_allow_html=True)