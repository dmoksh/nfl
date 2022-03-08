import nflfastpy
import pandas as pd
import streamlit as st  
import altair as alt
from pandasql import sqldf

#download play by play data

@st.cache()

def load_data():
    df = nflfastpy.load_pbp_data("2021")
    return df

#load data from nflfastpy
st.set_page_config(layout="wide")
df = load_data()

print(df.shape)
#filter for 3rd and 4th downs with pass attempts
df = df.loc[((df['down'] == 3) | (df['down'] == 4)) & ((df['play_type'] == 'pass') | (df['pass'] == 1))]

#now group by QB and count attemps (straight up count) and successful attempts (SUM(CASE WHEN (first_down_pass=1 or pass_touchdown=1) THEN 1 ELSE 0 END))
df = df.groupby(['passer_id','passer'], as_index=False).apply(lambda x: pd.Series({'attempts':x['down'].count(),
'successful_attempts':x.loc[(x.first_down_pass==1)|(x.pass_touchdown==1)]['down'].count(),
'total_yards':x['yards_gained'].sum(),
'qb_epa':x['qb_epa'].sum()}))

df['success_percent'] = round((df['successful_attempts']/df['attempts'])*100,2)

st.dataframe(df)

c = alt.Chart(df).mark_circle().encode(
     x='successful_attempts', y='attempts', size='success_percent', color='successful_attempts', tooltip=['attempts', 'successful_attempts','passer','success_percent'])

st.altair_chart(c, use_container_width=True)
