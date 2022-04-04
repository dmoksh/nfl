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
    df = df[['game_id','drive_number_for_game','drive_number_for_season','yards_gained_plus_penalty','ydsnet']]
    #df.to_csv("df.csv")
    #group by and sum up yards for the drive.
    df = df.groupby(['game_id','drive_number_for_game','drive_number_for_season'], as_index=False).apply(lambda x: pd.Series({'drive_yards':x['ydsnet'].max()}))
    #create rolling 7 drive sum
    df['rolling_7_drive_sum_yards_gained'] = df['drive_yards'].rolling(7).sum()
    return df

def get_data_for_post_season_second_half(df):
    #filter down to post season and 2nd half and overtime
    df = df[(df["season_type"] =="POST") & (df["game_half"]!='Half1')]
    #remove rows where drive is null
    df = df[df['drive'].notna()]    
    #group by game_id,posteam,drive and get max(ydsnet) - unfortunately there is no good way to 
    df = df.groupby(['game_id','posteam','drive'], as_index=False).apply(lambda x: pd.Series({'drive_yards':x['ydsnet'].max()
    ,'drive_first_downs':x['drive_first_downs'].max()
    ,'drive_pass_touchdowns':x['pass_touchdown'].sum()
    ,'drive_rush_touchdowns':x['rush_touchdown'].sum()}))
    df["touchdowns"] = df["drive_pass_touchdowns"] + df["drive_rush_touchdowns"]
    print(df)
    df = df.groupby(['game_id','posteam'], as_index=False).apply(lambda x: pd.Series({'2nd_half_yards':x['drive_yards'].sum()
    ,'2nd_half_drives':x['drive'].nunique()
    ,'2nd_half_first_downs':x['drive_first_downs'].sum()
    ,'2nd_half_touchdowns':x['touchdowns'].sum()}))
    df["2nd_half_yards_per_drive"] = df["2nd_half_yards"]/df["2nd_half_drives"]
    df = df[['game_id','posteam','2nd_half_yards','2nd_half_drives','2nd_half_yards_per_drive','2nd_half_first_downs','2nd_half_touchdowns']]
    df = df.rename(columns={'posteam': 'offense'})
    #df.sort_values(by=['yards_per_drive'],ascending=True)
    return df


#set streamlit page settings - this should be first command
st.set_page_config(layout="wide", page_icon="🏈", page_title="Chiefs' 2nd Half Offense in 2021 AFC Title Game")
st.title("2021 NFL Postseason - 2nd half + overtime offense stats")

#load data from nflfastpy
df = load_data()

#compile stats for 2nd half
df = get_data_for_post_season_second_half(df = df)

st.dataframe(df)
st.write(""" I wanted to see what went wrong for Chiefs in 2nd half of AFC Championship game and complied these stats. Here are some interesting facts i noticed""")
st.write("""* Chiefs had the lowest yards per drive of at 11.85 - 75 percent drop from a week before against bills, where they had 49.14 yards per drive.""")
st.write("* Greenbay had the lowest yards at 48. How does this happen with Rodgers and DeVante?")
st.write("* Chiefs and Greenbay, teams with top 2 lowest yards in the second of postseason, traded their WR1")
st.write("* The final kneeldown in the superbowl meant both LA and CIN ended with same drives and yards - 7 and 136")   

