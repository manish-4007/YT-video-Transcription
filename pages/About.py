import streamlit as st 

with open("README.md", 'r',encoding="utf8") as f:
    readme_line = f.read()
    
st.markdown(readme_line,unsafe_allow_html=True)