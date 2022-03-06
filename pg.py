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
#df.to_sql("last_year",engine,schema="nfl",if_exists="replace")

pysqldf = lambda q: sqldf(q, globals())

qb_eff_df = pysqldf("""select 
passer_player_id,passer_player_name,
SUM(1) as attempts,
SUM(CASE WHEN (first_down_pass=1 or pass_touchdown=1) THEN 1 ELSE 0 END) as successful_attempts,
CAST(ROUND((CAST(SUM(CASE WHEN (first_down_pass=1 or pass_touchdown=1) THEN 1 ELSE 0 END) as decimal)/CAST(SUM(1) as decimal))*100,2) as decimal) as efficiency
from df
where  down in (3,4) and play_type_nfl like 'PASS' and pass = 1
group by passer_player_id,passer_player_name
order by successful_attempts desc;""")

print(qb_eff_df.info(),qb_eff_df)
#st.dataframe(qb_eff_df)

