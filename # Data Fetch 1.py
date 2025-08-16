# Data Fetch

# Required Libraries
import os
import json
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# ---------- Helper Function ----------
def clean_states_column(df):
    """Cleans and standardizes the 'states' column if it exists."""
    if not df.empty and 'states' in df.columns:
        df['states'] = df['states'].str.replace('andaman-&-nicobar-islands','Andaman & Nicobar')
        df['states'] = df['states'].str.replace('-',' ')
        df['states'] = df['states'].str.title()
        df['states'] = df['states'].str.replace(
            'Dadra & Nagar Haveli & Daman & Diu',
            'Dadra and Nagar Haveli and Daman and Diu'
        )
    return df


# ------------------Table 1--------------------------
agg_ins_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\aggregated\insurance\country\india\state"
agg_ins_list = os.listdir(agg_ins_path) if os.path.exists(agg_ins_path) else []

table_1 = []
for i in agg_ins_list:
    state1 = os.path.join(agg_ins_path, i)
    for j in os.listdir(state1):
        years1 = os.path.join(state1, j)
        for k in os.listdir(years1):
            qtr1 = os.path.join(years1, k)
            with open(qtr1, "r") as f:
                J = json.load(f)
            for n in J["data"]["transactionData"]:
                insurance = n["name"]
                count = n['paymentInstruments'][0]['count']
                amount = n['paymentInstruments'][0]["amount"]
                table_1.append({
                    'states': i,
                    'years': j,
                    'quarter': int(k.strip('.json')),
                    'transaction_type': insurance,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table1 = pd.DataFrame(table_1)
df_table1 = clean_states_column(df_table1)

df_table1.to_csv('table1.csv', index=False)

# SQL DATABASE CONNECTION
url = "postgresql://neondb_owner:npg_bpCADu5V4PsM@ep-purple-bird-a1wedpb9.ap-southeast-1.aws.neon.tech/phonepe_pulse?sslmode=require&channel_binding=require"
engine = create_engine(url)

df_table1.to_sql('agg_ins', engine, if_exists='replace', index=False)


# ------------------Table 2--------------------------
agg_trans_path = r'D:\DS-Projects\Phonepe\Exercise\pulse\data\aggregated\transaction\country\india\state'
agg_trans_list = os.listdir(agg_trans_path) if os.path.exists(agg_trans_path) else []

table_2 = []
for i in agg_trans_list:
    state2 = os.path.join(agg_trans_path, i)
    for j in os.listdir(state2):
        years2 = os.path.join(state2, j)
        for k in os.listdir(years2):
            qtr2 = os.path.join(years2, k)
            with open(qtr2, "r") as f:
                J = json.load(f)
            for m in J["data"]["transactionData"]:
                transaction = m["name"]
                count = m['paymentInstruments'][0]['count']
                amount = m['paymentInstruments'][0]["amount"]
                table_2.append({
                    'states': i,
                    'years': j,
                    'quarter': int(k.strip('.json')),
                    'transaction_type': transaction,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table2 = pd.DataFrame(table_2)
df_table2 = clean_states_column(df_table2)

df_table2.to_csv('table2.csv', index=False)
df_table2.to_sql('agg_trans', engine, if_exists='replace', index=False)


# ------------------Table 3--------------------------
agg_user_path = r'D:\DS-Projects\Phonepe\Final\pulse\data\aggregated\user\country\india\state'
agg_user_list = os.listdir(agg_user_path) if os.path.exists(agg_user_path) else []

table_3 = []
for i in agg_user_list:
    state3 = os.path.join(agg_user_path, i)
    for j in os.listdir(state3):
        years3 = os.path.join(state3, j)
        for k in os.listdir(years3):
            qtr3 = os.path.join(years3, k)
            with open(qtr3, "r") as f:
                J = json.load(f)

            user = J["data"]["aggregated"].get("registeredUsers")
            app = J["data"]["aggregated"].get("appOpens")

            try:
                for n in J['data']['usersByDevice']:
                    brand = n['brand']
                    count = n['count']
                    percent = n['percentage']
                    table_3.append({
                        'states': i,
                        'years': j,
                        'quarter': int(k.strip('.json')),
                        'registered_users': user,
                        'app_opens': app,
                        'brand': brand,
                        'transaction_count': count,
                        'percentage': percent
                    })
            except:
                pass

df_table3 = pd.DataFrame(table_3)
df_table3 = clean_states_column(df_table3)

df_table3.to_csv('table3.csv', index=False)
df_table3.to_sql('agg_user', engine, if_exists='replace', index=False)


# ------------------Table 4--------------------------
map_ins_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\map\insurance\hover\country\india\state"
map_ins_list = os.listdir(map_ins_path) if os.path.exists(map_ins_path) else []

table_4 = []
for i in map_ins_list:
    state4 = os.path.join(map_ins_path, i)
    for j in os.listdir(state4):
        years4 = os.path.join(state4, j)
        for k in os.listdir(years4):
            qtr4 = os.path.join(years4, k)
            with open(qtr4, 'r') as f:
                data = json.load(f)
            for n in data['data']['hoverDataList']:
                name = n['name']
                count = n['metric'][0]['count']
                amount = n['metric'][0]['amount']
                table_4.append({
                    'states': i,
                    "years": j,
                    'quarter': int(k.strip('.json')),
                    'districts': name,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table4 = pd.DataFrame(table_4)
df_table4 = clean_states_column(df_table4)

df_table4.to_csv('table4.csv', index=False)
df_table4.to_sql('map_ins', engine, if_exists='replace', index=False)


# ------------------Table 5--------------------------
map_trans_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\map\transaction\hover\country\india\state"
map_trans_list = os.listdir(map_trans_path) if os.path.exists(map_trans_path) else []

table_5 = []
for i in map_trans_list:
    state5 = os.path.join(map_trans_path, i)
    for j in os.listdir(state5):
        years5 = os.path.join(state5, j)
        for k in os.listdir(years5):
            qtr5 = os.path.join(years5, k)
            with open(qtr5, 'r') as f:
                data = json.load(f)
            for n in data['data']['hoverDataList']:
                name = n['name']
                count = n['metric'][0]['count']
                amount = n['metric'][0]['amount']
                table_5.append({
                    'states': i,
                    "years": j,
                    'quarter': int(k.strip('.json')),
                    'districts': name,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table5 = pd.DataFrame(table_5)
df_table5 = clean_states_column(df_table5)

df_table5.to_csv('table5.csv', index=False)
df_table5.to_sql('map_trans', engine, if_exists='replace', index=False)


# ------------------Table 6--------------------------
map_user_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\map\user\hover\country\india\state"
map_user_list = os.listdir(map_user_path) if os.path.exists(map_user_path) else []

table_6 = []
for i in map_user_list:
    state6 = os.path.join(map_user_path, i)
    for j in os.listdir(state6):
        years6 = os.path.join(state6, j)
        for k in os.listdir(years6):
            qtr6 = os.path.join(years6, k)
            with open(qtr6, "r") as f:
                J = json.load(f)
            try:
                for n in J['data']['hoverData'].items():
                    districts = n[0]
                    regusers = n[1]['registeredUsers']
                    appopens = n[1]['appOpens']
                    table_6.append({
                        'states': i,
                        "years": j,
                        'quarter': int(k.strip('.json')),
                        'districts': districts,
                        'registered_users': regusers,
                        'app_opens': appopens,
                    })
            except:
                pass

df_table6 = pd.DataFrame(table_6)
df_table6 = clean_states_column(df_table6)

df_table6.to_csv('table6.csv', index=False)
df_table6.to_sql('map_user', engine, if_exists='replace', index=False)


# ------------------Table 7--------------------------
top_ins_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\top\insurance\country\india\state"
top_ins_list = os.listdir(top_ins_path) if os.path.exists(top_ins_path) else []

table_7 = []
for i in top_ins_list:
    state7 = os.path.join(top_ins_path, i)
    for j in os.listdir(state7):
        years7 = os.path.join(state7, j)
        for k in os.listdir(years7):
            qtr7 = os.path.join(years7, k)
            with open(qtr7, "r") as f:
                J = json.load(f)
            for n in J["data"]["pincodes"]:
                name = n['entityName']
                count = n['metric']['count']
                amount = n['metric']['amount']
                table_7.append({
                    'states': i,
                    "years": j,
                    'quarter': int(k.strip('.json')),
                    'pincodes': name,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table7 = pd.DataFrame(table_7)
df_table7 = clean_states_column(df_table7)

df_table7.to_csv('table7.csv', index=False)
df_table7.to_sql('top_ins', engine, if_exists='replace', index=False)


# ------------------Table 8--------------------------
top_trans_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\top\transaction\country\india\state"
top_trans_list = os.listdir(top_trans_path) if os.path.exists(top_trans_path) else []

table_8 = []
for i in top_trans_list:
    state8 = os.path.join(top_trans_path, i)
    for j in os.listdir(state8):
        years8 = os.path.join(state8, j)
        for k in os.listdir(years8):
            qtr8 = os.path.join(years8, k)
            with open(qtr8, "r") as f:
                J = json.load(f)
            for n in J["data"]["pincodes"]:
                name = n['entityName']
                count = n['metric']['count']
                amount = n['metric']['amount']
                table_8.append({
                    'states': i,
                    "years": j,
                    'quarter': int(k.strip('.json')),
                    'pincodes': name,
                    'transaction_count': count,
                    'transaction_amount': amount
                })

df_table8 = pd.DataFrame(table_8)
df_table8 = clean_states_column(df_table8)

df_table8.to_csv('table8.csv', index=False)
df_table8.to_sql('top_trans', engine, if_exists='replace', index=False)


# ------------------Table 9--------------------------
top_user_path = r"D:\DS-Projects\Phonepe\Final\pulse\data\top\user\country\india\state"
top_user_list = os.listdir(top_user_path) if os.path.exists(top_user_path) else []

table_9 = []
for i in top_user_list:
    state9 = os.path.join(top_user_path, i)
    for j in os.listdir(state9):
        years9 = os.path.join(state9, j)
        for k in os.listdir(years9):
            qtr9 = os.path.join(years9, k)
            with open(qtr9, "r") as f:
                J = json.load(f)
            for n in J["data"]["pincodes"]:
                name = n['name']
                regusers = n['registeredUsers']
                table_9.append({
                    'states': i,
                    "years": j,
                    'quarter': int(k.strip('.json')),
                    'pincodes': name,
                    'registered_users': regusers
                })

df_table9 = pd.DataFrame(table_9)
df_table9 = clean_states_column(df_table9)

df_table9.to_csv('table9.csv', index=False)
df_table9.to_sql('top_user', engine, if_exists='replace', index=False)


# --------------------------Its Completed-----------------------------------
# Developed By : Bilk Edison Xavier
# Github : https://github.com/bilkedisonxavier
# email : edisonxavier44@gmail.com
# LinkedIn : www.linkedin.com/in/bilk-edison-xavier-1a9767344
