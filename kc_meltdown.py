import streamlit as st
import pandas as pd
import nflfastpy

@st.cache()
def load_data():
    #download play by play data
    df = nflfastpy.load_pbp_data("2021")
    return df

def get_data_for_7_drive_rolling_average(df):
    #get only Chief's offense rows
    df = df[df["posteam"] =="KC"]
    #remove rows where drive is null
    df = df[df['drive'].notna()]
    #add a new column to show drive number for the game - in sql terms dense rank partitioned by game_id
    df['drive_number_for_game'] = (df.groupby('game_id')['drive']
                      .rank(method='dense', ascending=True)
                      .astype(int)
                   )
    #add a new column to show drive number for season - in sql terms dense rank over the entire table.
    df["drive_number_for_season"] = df[["game_id","drive"]].apply(tuple,axis=1)\
             .rank(method='dense',ascending=True).astype(int)
    #add a new column to get accurate yards gained by penalty - offense + penalty yards
    df['yards_gained_plus_penalty'] = df['yards_gained'].fillna(0) + df['penalty_yards'].fillna(0)
    #remove unwanted columns
    df = df[['game_id','drive_number_for_game','drive_number_for_season','yards_gained_plus_penalty']]
    #df.to_csv("df.csv")
    #group by and sum up yards for the drive.
    df = df.groupby(['game_id','drive_number_for_game','drive_number_for_season'], as_index=False).apply(lambda x: pd.Series({'drive_yards':x['yards_gained_plus_penalty'].sum()}))
    #create rolling 7 drive sum
    df['rolling_7_drive_sum_yards_gained'] = df['drive_yards'].rolling(7).sum()
    return df



#set streamlit page settings - this should be first command
st.set_page_config(layout="wide", page_icon="🏈", page_title="Chiefs' 2nd Half Offense in 2021 AFC Title Game")
st.title("Chiefs Offense - 2nd Half of AFC title game - 7 Drives | 83 Yards")

#load data from nflfastpy
df = load_data()

#get data from 7 drive rolling average
df1 = get_data_for_7_drive_rolling_average(df = df)




st.write("""That doesn't sound right, especially with Mahomes at helm, so i wanted to see how bad was it. 
Compiled a rolling sum yards for any given 7 drives in 2021 and could find only 2 instances where they scored less:""")

st.write('* Week 5 against GB - 77 yards - that was a bad game 😖')
st.write('* Drives spread across week 13 and 14 - not counting this because, week 13 game ended with KC taking knee')


#df1.sort_values(by=['rolling_7_drive_sum_yards_gained'],ascending=True,inplace=True)
st.dataframe(df1)

