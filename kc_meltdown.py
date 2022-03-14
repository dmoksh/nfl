import streamlit as st
import pandas as pd
import nflfastpy

def load_data():
    #download play by play data
    df = nflfastpy.load_pbp_data("2021")
    return df

#set streamlit page settings - this should be first command
st.set_page_config(layout="wide", page_icon="🏈", page_title="Chiefs' 2nd Half Offense in 2021 AFC Title Game")

#load data from nflfastpy
df = load_data()



