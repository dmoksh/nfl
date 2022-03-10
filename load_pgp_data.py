import nflfastpy
import pandas
from sqlalchemy import create_engine
import streamlit as st  
from pandasql import sqldf

#download play by play data
df = nflfastpy.load_pbp_data("2021")

#connection string to local database
engine = create_engine('postgresql://dinu:@localhost:5432/dinu')

#load df into the table.
df.to_sql("last_year",engine,schema="nfl",if_exists="replace")






