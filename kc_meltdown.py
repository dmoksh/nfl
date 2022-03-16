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

df = df[['game_id','drive_number_for_game','drive_number_for_season','yards_gained']]
df.to_csv("df.csv")
#df['drive_yards'] = df['yards_gained'].groupby(df[['game_id','drive_number_for_game','drive_number_for_season']]).transform('sum')
#now group by QB and count attemps (straight up count) and successful attempts (SUM(CASE WHEN (first_down_pass=1 or pass_touchdown=1) THEN 1 ELSE 0 END))
df1 = df.groupby(['game_id','drive_number_for_game','drive_number_for_season'], as_index=False).apply(lambda x: pd.Series({'drive_yards':x['yards_gained'].sum()}))
df1['rolling_7_drive_sum_yards_gained'] = df1['drive_yards'].rolling(7).sum()
df1.to_csv("df_agg.csv")


st.subheader("Chiefs' offensive production in 2nd half and overtime - 83 yards")
st.write("""That doesn't sound right, especially with Mahomes at helm, so i wanted to see how bad was it. 
Compiled a rolling sum yards for any given 7 drives in 2021 and only once did they score less than this - 77 against GB in week 5""")

#df1.sort_values(by=['rolling_7_drive_sum_yards_gained'],ascending=True,inplace=True)
st.dataframe(df1)

