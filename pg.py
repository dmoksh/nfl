import nflfastpy
import pandas
from sqlalchemy import create_engine
import streamlit as st  
from pandasql import sqldf
import pandas as pd

#download play by play data
df = nflfastpy.load_pbp_data("2021")

df = df.loc[((df['down'] == 3) | (df['down'] == 4)) & ((df['play_type'] == 'pass') | (df['pass'] == 1))]


df = df.groupby(['passer_id','passer'], as_index=False).apply(lambda x: pd.Series({'attempts':x['down'].count(),
    'successful_attempts':x.loc[(x.first_down_pass==1)|(x.pass_touchdown==1)]['down'].count(),
    'total_yards':x['yards_gained'].sum(),
    'qb_epa':x['qb_epa'].sum(),
    'touchdowns':x['touchdown'].sum()}))

df['success_percent'] = round((df['successful_attempts']/df['attempts'])*100,2)
#df.sort_values(by=['successful_attempts'],ascending=False,inplace=True)

print(df.iloc[df['attempts'].idxmax()]['passer'])
print(df.iloc[df['successful_attempts'].idxmax()]['passer'])
print(df.iloc[df['total_yards'].idxmax()]['passer'])
print(df.iloc[df['touchdowns'].idxmax()]['passer'])








