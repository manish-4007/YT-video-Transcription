import streamlit as st 

with open("README.md", 'r') as f:
    st.markdown(f.read(), unsafe_allow_html=True)