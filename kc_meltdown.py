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
print(df.shape)
st.title("Chiefs Offence - 2nd Half of AFC title game")

#get only Chief's offense rows
df = df[df["posteam"] =="KC"]

#remove rows where drive is null
df = df[df['drive'].notna()]
print(df.shape)

#add a new column to show drive number for the game
df['drive_number_for_game'] = (df.groupby('game_id')['drive']
                      .rank(method='dense', ascending=True)
                      .astype(int)
                   )


#add a new column to show drive number for season
df["drive_number_for_season"] = df[["game_id","drive"]].apply(tuple,axis=1)\
             .rank(method='dense',ascending=True).astype(int)

#df['drive_yards'] = df['yards_gained'].groupby(df[['game_id','drive_number_for_season']]).transform('sum')
df.to_csv("df.csv")







