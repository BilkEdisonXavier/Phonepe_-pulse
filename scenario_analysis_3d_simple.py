
# Use Case Scenario Analysis — 3D Views
# -------------------------------------------------------------
# Required Libraries
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import plotly.express as px

# SQL DATABASE CONNECTION
url = "postgresql://neondb_owner:npg_bpCADu5V4PsM@ep-purple-bird-a1wedpb9.ap-southeast-1.aws.neon.tech/phonepe_pulse?sslmode=require"
engine = create_engine(url)

# -----------------------Scenario 1-----------------------------

# Query 1: Transaction Dynamics Across States
q1 = """SELECT states, SUM(transaction_count) AS total_transaction_count,
               SUM(transaction_amount) AS total_transaction_amount
        FROM agg_trans GROUP BY states ORDER BY total_transaction_amount DESC"""
df1 = pd.read_sql_query(q1, engine)
fig1 = px.scatter_3d(df1, x="states", y="total_transaction_count", z="total_transaction_amount",
                     color="states", size="total_transaction_amount",
                     title="3D Transactions Across States")
fig1.show()

# Query 2: Transaction Dynamics Over Quarters
q2 = """SELECT years, quarter, SUM(transaction_count) AS total_transaction_count,
               SUM(transaction_amount) AS total_transaction_amount
        FROM agg_trans GROUP BY years, quarter ORDER BY years, quarter"""
df2 = pd.read_sql_query(q2, engine)
fig2 = px.scatter_3d(df2, x="years", y="quarter", z="total_transaction_amount",
                     size="total_transaction_count", color="years",
                     title="3D Transactions Over Time (Years × Quarter × Amount)")
fig2.show()

# Query 3: Transaction Dynamics by Payment Category
q3 = """SELECT transaction_type, SUM(transaction_count) AS total_trans_count,
               SUM(transaction_amount) AS total_amount
        FROM agg_trans GROUP BY transaction_type ORDER BY total_amount DESC"""
df3 = pd.read_sql_query(q3, engine)
fig3 = px.scatter_3d(df3, x="transaction_type", y="total_trans_count", z="total_amount",
                     color="transaction_type", size="total_amount",
                     title="3D Transactions by Payment Category")
fig3.show()

# Query 4: Consistent Growth Across States
q4 = """SELECT states, years, quarter, SUM(transaction_amount) AS total_amount
        FROM agg_trans GROUP BY states, years, quarter ORDER BY states, years, quarter"""
df4 = pd.read_sql_query(q4, engine)
fig4 = px.line_3d(df4, x="years", y="quarter", z="total_amount", color="states",
                  title="3D Growth Trajectory Across States")
fig4.show()

# Query 5: Growth by Transaction Type
q5 = """SELECT transaction_type, years, quarter, SUM(transaction_amount) AS transaction_amount
        FROM agg_trans GROUP BY transaction_type, years, quarter
        ORDER BY transaction_type, years, quarter"""
df5 = pd.read_sql_query(q5, engine)
fig5 = px.line_3d(df5, x="years", y="quarter", z="transaction_amount", color="transaction_type",
                  title="3D Growth by Transaction Type")
fig5.show()

# -------------------------- Scenario 2-------------------------

# Query 6: Device Dominance
q6 = """SELECT brand, SUM(registered_users) AS total_users
        FROM agg_user GROUP BY brand ORDER BY total_users DESC"""
df6 = pd.read_sql_query(q6, engine)
fig6 = px.scatter_3d(df6, x="brand", y="total_users", z="total_users", size="total_users", color="brand",
                     title="3D Device Dominance by Brand")
fig6.show()

# Query 7: User Engagement
q7 = """SELECT brand, SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_opens,
               ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 4) AS engagement_rate
        FROM agg_user GROUP BY brand ORDER BY engagement_rate DESC"""
df7 = pd.read_sql_query(q7, engine)
fig7 = px.scatter_3d(df7, x="brand", y="total_users", z="engagement_rate", size="total_users", color="brand",
                     title="3D User Engagement by Brand")
fig7.show()

# Query 8: Underutilized Devices
q8 = """SELECT brand, states, SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_opens,
               ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 4) AS engagement_rate
        FROM agg_user GROUP BY brand, states
        HAVING ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 4) < 0.3
           AND SUM(registered_users) > 500000 ORDER BY engagement_rate ASC"""
df8 = pd.read_sql_query(q8, engine)
fig8 = px.scatter_3d(df8, x="brand", y="total_users", z="engagement_rate", color="states",
                     size="total_users", title="3D Underutilized Devices by State & Brand")
fig8.show()

# Query 9: Region-Wise Engagement
q9 = """SELECT states, brand, SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_opens,
               ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 4) AS engagement_rate
        FROM agg_user GROUP BY states, brand ORDER BY states, engagement_rate DESC"""
df9 = pd.read_sql_query(q9, engine)
fig9 = px.scatter_3d(df9, x="states", y="brand", z="engagement_rate",
                     size="total_users", color="states",
                     title="3D Region-wise Engagement by Brand")
fig9.show()

# Query 10: Quarterly Trends
q10 = """SELECT years, quarter, brand, SUM(registered_users) AS total_users,
                SUM(app_opens) AS total_opens,
                ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 4) AS engagement_rate
         FROM agg_user GROUP BY years, quarter, brand ORDER BY years, quarter, engagement_rate DESC"""
df10 = pd.read_sql_query(q10, engine)
fig10 = px.line_3d(df10, x="years", y="quarter", z="engagement_rate", color="brand",
                   title="3D Quarterly Engagement Trends by Brand")
fig10.show()

# ----------------------------- Scenario 3---------------------------

# Query 11: State Ranking by Insurance Volume & Value
q11 = """SELECT states, SUM(transaction_count) AS total_ins_count,
                SUM(transaction_amount) AS total_ins_amount
         FROM agg_trans GROUP BY states ORDER BY total_ins_amount DESC"""
df11 = pd.read_sql_query(q11, engine)
fig11 = px.scatter_3d(df11, x="states", y="total_ins_count", z="total_ins_amount",
                      size="total_ins_amount", color="states",
                      title="3D State Ranking by Insurance Volume & Value")
fig11.show()

# Query 12: Quarterly & Yearly Growth Trajectory
q12 = """SELECT states, years, quarter, cnt, amt,
                ROUND(((amt - LAG(amt) OVER (PARTITION BY states ORDER BY years, quarter)) /
                      NULLIF(LAG(amt) OVER (PARTITION BY states ORDER BY years, quarter),0))::numeric,4) AS qoq_growth_pct,
                ROUND(((amt - LAG(amt) OVER (PARTITION BY states ORDER BY years)) /
                      NULLIF(LAG(amt) OVER (PARTITION BY states ORDER BY years),0))::numeric,4) AS yoy_growth_pct
         FROM (SELECT states, years, quarter,
                      SUM(transaction_count) AS cnt,
                      SUM(transaction_amount) AS amt
               FROM agg_ins GROUP BY states, years, quarter) AS subq
         ORDER BY states, years, quarter"""
df12 = pd.read_sql_query(q12, engine)
fig12 = px.line_3d(df12, x="years", y="quarter", z="amt", color="states",
                   title="3D Insurance Growth Trajectory by State")
fig12.show()

# Query 13: Fastest-Growing Insurance Markets
q13 = """SELECT states, years, quarter,
                ROUND(((amt - prev_amt) / NULLIF(prev_amt, 0))::numeric, 4) AS growth_pct
         FROM (SELECT states, years, quarter, SUM(transaction_amount) AS amt,
                      LAG(SUM(transaction_amount)) OVER (PARTITION BY states ORDER BY years, quarter) AS prev_amt
               FROM agg_ins GROUP BY states, years, quarter) AS growth
         WHERE prev_amt IS NOT NULL ORDER BY growth_pct DESC LIMIT 10"""
df13 = pd.read_sql_query(q13, engine)
fig13 = px.scatter_3d(df13, x="states", y="years", z="growth_pct", color="quarter",
                      size="growth_pct", title="3D Fastest Growing Insurance Markets")
fig13.show()

# ------------------------------Scenario 4------------------------------------

# Query 14: Transaction analysis by top-performing states
q14 = """SELECT states, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM agg_trans GROUP BY states ORDER BY total_value DESC, total_txn DESC LIMIT 1"""
df14 = pd.read_sql_query(q14, engine)
fig14 = px.scatter_3d(df14, x="states", y="total_txn", z="total_value",
                      size="total_value", color="states",
                      title="3D Top Performing States (Transactions)")
fig14.show()

# Query 15: Transaction analysis by top-performing Districts
q15 = """SELECT districts, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM map_trans GROUP BY districts ORDER BY total_value DESC, total_txn DESC"""
df15 = pd.read_sql_query(q15, engine)
fig15 = px.scatter_3d(df15, x="districts", y="total_txn", z="total_value",
                      size="total_value", color="districts",
                      title="3D Transactions by Districts")
fig15.show()

# Query 16: Transaction analysis by top-performing Pincodes
q16 = """SELECT pincodes, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM top_trans GROUP BY pincodes ORDER BY total_value DESC, total_txn DESC LIMIT 10"""
df16 = pd.read_sql_query(q16, engine)
fig16 = px.scatter_3d(df16, x="pincodes", y="total_txn", z="total_value",
                      size="total_value", color="pincodes",
                      title="3D Transactions by Top Pincodes")
fig16.show()

# ---------------------------Scenario 5------------------------------------------

# Query 17: User Registration Analysis by top states
q17 = """SELECT states, SUM(registered_users) AS total_users
         FROM agg_user GROUP BY states ORDER BY total_users DESC LIMIT 10"""
df17 = pd.read_sql_query(q17, engine)
fig17 = px.scatter_3d(df17, x="states", y="total_users", z="total_users",
                      size="total_users", color="states",
                      title="3D Top States by User Registration")
fig17.show()

# Query 18: User Registration Analysis by top districts
q18 = """SELECT districts, SUM(registered_users) AS total_users
         FROM map_user GROUP BY districts ORDER BY total_users DESC LIMIT 1"""
df18 = pd.read_sql_query(q18, engine)
fig18 = px.scatter_3d(df18, x="districts", y="total_users", z="total_users",
                      size="total_users", color="districts",
                      title="3D Top Districts by User Registration")
fig18.show()

# Query 19: User Registration Analysis by top pincodes
q19 = """SELECT pincodes, SUM(registered_users) AS total_users
         FROM top_user GROUP BY pincodes ORDER BY total_users DESC LIMIT 10"""
df19 = pd.read_sql_query(q19, engine)
fig19 = px.scatter_3d(df19, x="pincodes", y="total_users", z="total_users",
                      size="total_users", color="pincodes",
                      title="3D Top Pincodes by User Registration")
fig19.show()

# -----------------------------Scenario 6-----------------------

# Query 20: Insurance Transactions Analysis Top States
q20 = """SELECT states, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM agg_ins GROUP BY states ORDER BY total_value DESC, total_txn DESC LIMIT 10"""
df20 = pd.read_sql_query(q20, engine)
fig20 = px.scatter_3d(df20, x="states", y="total_txn", z="total_value",
                      size="total_value", color="states",
                      title="3D Top States by Insurance Transactions")
fig20.show()

# Query 21: Insurance Transactions Analysis Top Districts
q21 = """SELECT districts, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM map_ins GROUP BY districts ORDER BY total_value DESC, total_txn DESC LIMIT 10"""
df21 = pd.read_sql_query(q21, engine)
fig21 = px.scatter_3d(df21, x="districts", y="total_txn", z="total_value",
                      size="total_value", color="districts",
                      title="3D Top Districts by Insurance Transactions")
fig21.show()

# Query 22: Insurance Transactions Analysis Top Pincodes
q22 = """SELECT pincodes, SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
         FROM top_ins GROUP BY pincodes ORDER BY total_value DESC, total_txn DESC LIMIT 10"""
df22 = pd.read_sql_query(q22, engine)
fig22 = px.scatter_3d(df22, x="pincodes", y="total_txn", z="total_value",
                      size="total_value", color="pincodes",
                      title="3D Top Pincodes by Insurance Transactions")
fig22.show()

# -------------------------------------------------------------
# Developed By :
# Bilk Edison Xavier
# Github :https://github.com/bilkedisonxavier
# email: edisonxavier44@gmail.com
# LinkedIn : www.linkedin.com/in/bilk-edison-xavier-1a9767344
