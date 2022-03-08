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
st.set_page_config(layout="centered", page_icon="🏈", page_title="QB's on 3rd and 4th downs")
df = load_data()

#filter for 3rd and 4th downs with pass attempts
df = df.loc[((df['down'] == 3) | (df['down'] == 4)) & ((df['play_type'] == 'pass') | (df['pass'] == 1))]

#now group by QB and count attemps (straight up count) and successful attempts (SUM(CASE WHEN (first_down_pass=1 or pass_touchdown=1) THEN 1 ELSE 0 END))
df = df.groupby(['passer_id','passer'], as_index=False).apply(lambda x: pd.Series({'attempts':x['down'].count(),
'successful_attempts':x.loc[(x.first_down_pass==1)|(x.pass_touchdown==1)]['down'].count(),
'total_yards':x['yards_gained'].sum(),
'qb_epa':x['qb_epa'].sum()}))

df['success_percent'] = round((df['successful_attempts']/df['attempts'])*100,2)

#title and captions
st.title("🏈 NFL QB Performance on 3rd and 4th downs")
st.caption("* An attempt is considered successful if it ends in firstdown or touchdown, with or without the help of penalties.")
st.caption("* Both regular and post season games")

#snippets
#st.write("Burrow has most attemps at 242 and Stafford most successful attempts at 99")
#st.write("For players above 100 attempts, Justin Fields has lowest sucessful attempts with 23")
st.metric(label="Most attempts - Burrow", value="242")
st.metric(label="Most successful attempts - Stafford", value="99")

#display the dataframe as table - remove passer_id
st.dataframe(df[['passer','attempts','successful_attempts','success_percent','qb_epa','total_yards']])

#plot to show attempts vs successful_attempts
st.subheader("Plot - Attempts vs Successful Attempts")
c = alt.Chart(df).mark_circle().encode(
     x='successful_attempts', y='attempts', size=alt.Size('success_percent',legend=None), color=alt.Color('passer', legend=None), tooltip=['attempts', 'successful_attempts','passer','success_percent'])


st.altair_chart(c, use_container_width=True)
