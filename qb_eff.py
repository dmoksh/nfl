import nflfastpy
from numpy import sort
import pandas as pd
import streamlit as st  
import altair as alt
from pandasql import sqldf
import plotly_express as px


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
'qb_epa':x['qb_epa'].sum(),
'touchdown':x['touchdown'].sum()}))

df['success_percent'] = round((df['successful_attempts']/df['attempts'])*100,2)

#sort df by successful_attemps descending - this is default
df.sort_values(by=['successful_attempts'],ascending=False,inplace=True)

#change df column types

df.attempts = df.attempts.astype(int)
df.successful_attempts = df.successful_attempts.astype(int)

#title and captions
st.title("🏈 QB Stats on 3rd and 4th downs")
st.caption("An attempt is considered successful if it ends in firstdown or touchdown, with or without the help of penalties.")
#st.caption("* Both regular and post season games")

#snippets with columns
#st.write("Burrow has most attemps at 242 and Stafford most successful attempts at 99")
#st.write("For players above 100 attempts, Justin Fields has lowest sucessful attempts with 23")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Most attempts - Burrow", value="242")
with col2:
    st.metric(label="Most successful attempts - Stafford", value="99")

col3, col4 = st.columns(2)
with col3:
    st.metric(label="Most yards - Stafford", value="1706")
with col4:
    st.metric(label="Most touchdowns - Stafford", value="22")

#display the dataframe as table - remove passer_id
st.subheader("Table - QB Stats on 3rd and 4th downs")
st.dataframe(df[['passer','attempts','successful_attempts','success_percent','qb_epa','total_yards','touchdown']])

#plot to show attempts vs successful_attempts
st.subheader("Plot - Attempts vs Successful Attempts")
c = alt.Chart(df).mark_circle().encode(
     x='successful_attempts', y='attempts', size=alt.Size('success_percent',legend=None), color=alt.Color('passer', legend=None), tooltip=['attempts', 'successful_attempts','passer','success_percent'])


st.altair_chart(c, use_container_width=True)



#chart to show qb_epa
df.sort_values(by=['qb_epa'],ascending=True,inplace=True)
st.subheader("Chart - QB EPA")
fig = px.bar(df, x='passer', y='qb_epa')
st.plotly_chart(figure_or_data=fig)