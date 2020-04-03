
# coding=utf-8
import streamlit as st
import yaml

import plotly.express as px
from streamlit import caching

import model_description as md
import fontes as ft
import simulation as sm

def main():
    pic = "https://static1.squarespace.com/static/5d86962ef8b1bc58c1dcaa0b/t/5ddad475ee3ebb607ae3d629/1584997792692/?format=1500w"
    st.sidebar.image(pic, use_column_width=False, width=100, caption=None)
    page = st.sidebar.selectbox("Menu", ["COVID19 no seu Município","Descição do Modelo","Fontes"])

    if page == "Descição do Modelo":
        if __name__ == "__main__":
            md.main()

    elif page=="Fontes":
        if __name__ == "__main__":
            ft.main()
        
    elif page == "COVID19 no seu Município":        
          if __name__ == "__main__":
            sm.main()          
            
 
if __name__ == "__main__":
    main()
    

