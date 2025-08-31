#lib
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import requests


# ---------------- Database Connection ----------------
# Using SQLAlchemy for a cleaner connection
engine = create_engine("postgresql+psycopg2://postgres:Edison@localhost:5432/phonepe")


# Helper function to fetch data
def fetch_data(query: str):
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
#streamlit app:
# Page setup

st.set_page_config(page_title="PhonePe Transaction Insights ", layout="wide")

# Top navigation bar
selected = option_menu(
    menu_title='Welcome To Phonepepulse',
    options=["🏠 Home", "📊 Pulse Insights", "📄 Docs"],
    icons=["house", "bar-chart-line", "file-earmark-text"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#3d1a6e"},
        "nav-link": {"color": "white", "font-size": "16px", "margin": "0 20px"},
        "nav-link-selected": {"color": "#a370f7", "font-weight": "bold"},
    }
)

# Section 1 - Home
if selected == "🏠 Home":
    
    st.title("📱PhonePe")


    # About PhonePe
    st.markdown("""
    **PhonePe** is one of India’s leading digital payment platforms that allows users to:
    
    - Send and receive money instantly via UPI 💸  
    - Recharge mobile phones, pay utility bills ⚡📱  
    - Shop online and offline with QR code scanning 🛒  
    - Invest in mutual funds, insurance, and more 📊  
      
    It powers **millions of transactions every day** and provides **insightful data**, which we explore here in this dashboard.
    """)

    st.success("Explore how India transacts with PhonePe Pulse 📊")

    st.markdown("---")
    st.markdown("🔍 Use the top menu to start exploring data or view documentation.")


# Section 2 - Data Analysis Dashboards
elif selected == "📊 Pulse Insights":
    st.title("📊 Explore Transaction Data Insights")

    # Sidebar - Choose Scenario
    scenario = st.sidebar.selectbox("📌 Select Scenario", [
        "1. Decoding Transaction Dynamics on PhonePe",
        "2. Insurance Engagement Analysis",
        "3. Insurance Penetration and Growth Potential Analysis",
        "4. User Registration Analysis",
        "5. Insurance Transactions Analysis"
    ])

# Scenario 1
    if scenario == "1. Decoding Transaction Dynamics on PhonePe":
        q = st.selectbox("Choose a Question", [
            "I. Transaction Dynamics Across States",
            "II. Transaction Dynamics Over Quarters",
            "III. Transaction Dynamics by Payment Category",
            "IV. Consistent Growth, Stagnation, or Decline Across States",
            "V. Consistent Growth, Stagnation, or Decline by Transaction Type"

        ])

        # Question I
        if q == "I. Transaction Dynamics Across States":
            st.subheader("📌 Transaction Dynamics Across States")

            q1 = """
            SELECT 
                States,
                SUM(Transaction_count) AS total_transaction_count, 
                SUM(Transaction_amount) AS total_transaction_amount 
            FROM aggregated_transaction
            GROUP BY States 
            ORDER BY Total_transaction_amount DESC
            """
            query = pd.read_sql_query(q1,engine)

            fig = px.bar(
                query,
                x='states',
                y='total_transaction_amount',
                title='total transaction amount by State',
                labels={'total_transaction_amount': 'Transaction amount (₹)', 'states': 'States'},
                hover_data=['total_transaction_count']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        # Question II
        elif q == "II. Transaction Dynamics Over Quarters":
            st.subheader("📌 Transaction Dynamics Over Quarters")

            q2 = """
            SELECT 
                Years, 
                Quarter, 
                SUM(Transaction_count) AS total_transaction_count,
                SUM(Transaction_amount) AS total_transaction_amount
            FROM aggregated_transaction
            GROUP BY Years, Quarter
            ORDER BY Years, Quarter
            """
            query = pd.read_sql_query(q2,engine)

            # Create 'period' column
            query['period'] = query['years'].astype(str) + ' Q' + query['quarter'].astype(str)

            fig = px.bar(
                query,
                x='period',
                y='total_transaction_amount',
                title='total transaction amount by Quarter',
                labels={'total_transaction_amount': 'Transaction amount (₹)', 'Period': 'Quarter'},
                hover_data=['total_transaction_count']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        #Question III
        elif q == "III. Transaction Dynamics by Payment Category":
            st.subheader("📌 Transaction Dynamics by Payment Category")

            q3 = """
            SELECT 
                Transaction_type, 
                SUM(Transaction_count) AS total_trans_count, 
                SUM(Transaction_amount) AS total_amount 
            FROM aggregated_transaction
            GROUP BY Transaction_type 
            ORDER BY Total_amount DESC
            """
            query = pd.read_sql_query(q3,engine)

            st.write("This chart shows which payment categories (like Recharge, Bills, Peer-to-Peer, etc.) drive the highest transaction amounts and volumes on PhonePe.")

            fig = px.bar(
                query,
                x='transaction_type',
                y='total_amount',
                title='total transaction amount by Payment Category',
                labels={'total_amount': 'Transaction amount (₹)', 'Transaction_type': 'Payment Category'},
                hover_data=['total_trans_count']
            )

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        #Question IV    
        elif q == "IV. Consistent Growth, Stagnation, or Decline Across States":
            st.subheader("📌 Consistent Growth, Stagnation, or Decline Across States")

            query = """
            SELECT 
                States, 
                Years,
                Quarter,
                SUM(Transaction_amount) AS Total_amount 
            FROM aggregated_transaction
            GROUP BY States, Years, Quarter 
            ORDER BY States, Years, Quarter
            """
            q4 = pd.read_sql_query(query,engine)

            # Create 'period' column for time series (e.g., "2021 Q1")
            q4['period'] = q4['years'].astype(str) + ' Q' + q4['quarter'].astype(str)

            st.write("This line chart shows how the total transaction amount in each state changes quarter by quarter. You can spot which states are growing consistently, and which ones are stagnant or declining.")

            fig = px.line(
                q4,
                x='period',
                y='total_amount',
                color='states',
                title='Transaction Growth Trend Across States (Quarterly)',
                labels={'total_amount': 'Transaction amount (₹)', 'Period': 'Quarter'},
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(q4)

        #Question V
        elif q == "V. Consistent Growth, Stagnation, or Decline by Transaction Type":
            st.subheader("📌 Consistent Growth, Stagnation, or Decline by Transaction Type")

            query = """
            SELECT 
                Transaction_type, 
                Years, 
                Quarter,
                SUM(Transaction_amount) AS Transaction_amount  
            FROM aggregated_transaction
            GROUP BY Transaction_type, Years, Quarter 
            ORDER BY Transaction_type, Years, Quarter
            """
            q5 = pd.read_sql_query(query,engine)

            # Create a time period column
            q5['period'] = q5['years'].astype(str) + ' Q' + q5['quarter'].astype(str)

            st.write("This chart shows how transaction amounts vary over time across different transaction types, helping us identify which categories are growing, stable, or declining.")

            fig = px.line(
                q5,
                x='period',
                y='transaction_amount',
                color='transaction_type',
                title='Transaction Trend by Payment Category Over Time',
                labels={'transaction_amount': 'Transaction amount (₹)', 'Period': 'Quarter'},
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(q5)

# Scenario 2
    if scenario == "2. Insurance Engagement Analysis":
        q = st.selectbox("Choose a Question", [
            "I. Insurance Transactions Across States",
            "II. Insurance Transactions Over Quarters",
            "III. Insurance Uptake by Insurance Type",
            "IV. Consistent Growth or Decline Across States",
            "V. Consistent Growth or Decline by Insurance Type"
        ])

        # Question I
        if q == "I. Insurance Transactions Across States":
            st.subheader("📌 Insurance Transactions Across States")

            q1 = """
            SELECT 
            states,
            SUM(transaction_count) AS total_transaction_count, 
            SUM(transaction_amount) AS total_transaction_amount 
            FROM aggregated_insurance
            GROUP BY states 
            ORDER BY total_transaction_amount DESC
            """
            query = pd.read_sql_query(q1, engine)

            fig = px.bar(
                query,
                x='states',
                y='total_transaction_amount',
                title='Total Insurance Transaction Amount by State',
                labels={'total_transaction_amount': 'Transaction Amount (₹)', 'states': 'States'},
                hover_data=['total_transaction_count']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        # Question II
        elif q == "II. Insurance Transactions Over Quarters":
            st.subheader("📌 Insurance Transactions Over Quarters")

            q2 = """
            SELECT 
                years, 
                quarter, 
                SUM(transaction_count) AS total_transaction_count,
                SUM(transaction_amount) AS total_transaction_amount
            FROM aggregated_insurance
            GROUP BY years, quarter
            ORDER BY years, quarter
            """
            query = pd.read_sql_query(q2, engine)

            query['period'] = query['years'].astype(str) + ' Q' + query['quarter'].astype(str)

            fig = px.bar(
                query,
                x='period',
                y='total_transaction_amount',
                title='Total Insurance Transaction Amount by Quarter',
                labels={'total_transaction_amount': 'Transaction Amount (₹)', 'period': 'Quarter'},
                hover_data=['total_transaction_count']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        # Question III
        elif q == "III. Insurance Uptake by Insurance Type":
            st.subheader("📌 Insurance Uptake by Insurance Type")

            q3 = """
            SELECT 
                insurance_type, 
                SUM(transaction_count) AS total_trans_count, 
                SUM(transaction_amount) AS total_amount 
            FROM aggregated_insurance
            GROUP BY insurance_type 
            ORDER BY total_amount DESC
            """
            query = pd.read_sql_query(q3, engine)

            st.write("This chart shows which insurance types (like Health, Life, Vehicle, etc.) have the highest uptake among users.")

            fig = px.bar(
                query,
                x='insurance_type',
                y='total_amount',
                title='Total Insurance Transaction Amount by Type',
                labels={'total_amount': 'Transaction Amount (₹)', 'insurance_type': 'Insurance Type'},
                hover_data=['total_trans_count']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        # Question IV
        elif q == "IV. Consistent Growth or Decline Across States":
            st.subheader("📌 Growth or Decline Across States")

            query = """
            SELECT 
                states, 
                years,
                quarter,
                SUM(transaction_amount) AS total_amount 
            FROM aggregated_insurance
            GROUP BY states, years, quarter 
            ORDER BY states, years, quarter
            """
            q4 = pd.read_sql_query(query, engine)

            q4['period'] = q4['years'].astype(str) + ' Q' + q4['quarter'].astype(str)

            st.write("This line chart shows how insurance transaction amounts in each state change quarter by quarter.")

            fig = px.line(
                q4,
                x='period',
                y='total_amount',
                color='states',
                title='Insurance Transaction Trend Across States (Quarterly)',
                labels={'total_amount': 'Transaction Amount (₹)', 'period': 'Quarter'},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(q4)

        # Question V
        elif q == "V. Consistent Growth or Decline by Insurance Type":
            st.subheader("📌 Growth or Decline by Insurance Type")

            query = """
            SELECT 
                insurance_type, 
                years, 
                quarter,
                SUM(transaction_amount) AS transaction_amount  
            FROM aggregated_insurance
            GROUP BY insurance_type, years, quarter 
            ORDER BY insurance_type, years, quarter
            """
            q5 = pd.read_sql_query(query, engine)

            q5['period'] = q5['years'].astype(str) + ' Q' + q5['quarter'].astype(str)

            st.write("This chart shows how transaction amounts vary over time across different insurance types, highlighting trends in user engagement.")

            fig = px.line(
                q5,
                x='period',
                y='transaction_amount',
                color='insurance_type',
                title='Insurance Transaction Trend by Type Over Time',
                labels={'transaction_amount': 'Transaction Amount (₹)', 'period': 'Quarter'},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(q5)

# Scenario 3

    elif scenario == "3. Insurance Penetration and Growth Potential Analysis":
        q = st.selectbox(
            "Choose a Question",
            ["I. Insurance Growth Across States",
            "II. Insurance Transactions by Districts",
            "III. Insurance Transactions by Pincodes"]
        )

    # Question I: State-Level Insurance Growth
        if q == "I. Insurance Growth Across States":
            st.subheader("📊 Insurance Growth Across States")

            sql = """
            SELECT
                states,
                SUM(transaction_count)  AS total_txn,
                SUM(transaction_amount) AS total_value
            FROM map_insurance
            GROUP BY states
            ORDER BY total_value DESC, total_txn DESC;
            """
            df = pd.read_sql_query(sql, engine)

        # Clean state names
            state_name_map = {
                'Andaman & Nicobar': 'Andaman & Nicobar Islands',
                'Andhra Pradesh': 'Andhra Pradesh',
                'Arunachal Pradesh': 'Arunachal Pradesh',
                'Assam': 'Assam',
                'Bihar': 'Bihar',
                'Chandigarh': 'Chandigarh',
                'Chhattisgarh': 'Chhattisgarh',
                'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
                'Delhi': 'Delhi',
                'Goa': 'Goa',
                'Gujarat': 'Gujarat',
                'Haryana': 'Haryana',
                'Himachal Pradesh': 'Himachal Pradesh',
                'Jammu & Kashmir': 'Jammu and Kashmir',
                'Jharkhand': 'Jharkhand',
                'Karnataka': 'Karnataka',
                'Kerala': 'Kerala',
                'Ladakh': 'Ladakh',
                'Lakshadweep': 'Lakshadweep',
                'Madhya Pradesh': 'Madhya Pradesh',
                'Maharashtra': 'Maharashtra',
                'Manipur': 'Manipur',
                'Meghalaya': 'Meghalaya',
                'Mizoram': 'Mizoram',
                'Nagaland': 'Nagaland',
                'Odisha': 'Odisha',
                'Puducherry': 'Puducherry',
                'Punjab': 'Punjab',
                'Rajasthan': 'Rajasthan',
                'Sikkim': 'Sikkim',
                'Tamil Nadu': 'Tamil Nadu',
                'Telangana': 'Telangana',
                'Tripura': 'Tripura',
                'Uttar Pradesh': 'Uttar Pradesh',
                'Uttarakhand': 'Uttarakhand',
                'West Bengal': 'West Bengal' 
            }
            df['state_clean'] = df['states'].map(state_name_map)
            df = df.dropna(subset=['state_clean'])

        # Load India GeoJSON
            geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            resp = requests.get(geojson_url)
            resp.raise_for_status()
            india_geojson = resp.json()

        # Choropleth map
            fig = px.choropleth(
                df,
                geojson=india_geojson,
                featureidkey="properties.ST_NM",
                locations="state_clean",
                color="total_value",
                color_continuous_scale="Purples",
                title="Insurance Market Growth Across States",
                hover_data={"total_txn": True, "total_value": True}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

    # Question II: District-Level Insurance
        elif q == "II. Insurance Transactions by Districts":
            st.subheader("🏙️ Insurance Transactions by Districts")

            q15 = """
            SELECT 
                districts, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM map_insurance
            GROUP BY districts 
            ORDER BY total_value DESC, total_txn DESC
            LIMIT 10;
            """
            query = pd.read_sql_query(q15, engine)

            fig = px.bar(
                query,
                x='districts',
                y='total_value',
                title='Top 10 Districts by Insurance Value',
                labels={'total_value': 'Insurance Value (₹)', 'districts': 'District'},
                hover_data=['total_txn']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

    # Question III: Pincode-Level Insurance
        elif q == "III. Insurance Transactions by Pincodes":
            st.subheader("📮 Insurance Transactions by Pincodes")

            q16 = """
            SELECT 
                pincodes, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM top_insurance
            GROUP BY pincodes 
            ORDER BY total_value DESC, total_txn DESC 
            LIMIT 10;
            """
            query = pd.read_sql_query(q16, engine)

            fig = px.bar(
                query,
                x='pincodes',
                y='total_value',
                title='Top 10 Pincodes by Insurance Value',
                labels={'pincodes': 'Pincode', 'total_value': 'Insurance Value (₹)'},
                hover_data=['total_txn']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

# Scenario 3
    elif scenario == "Transaction Analysis Across States and Districts":
        q = st.selectbox(
            "Choose a Question",
            ["I. Transaction Analysis by States",
            "II. Transaction Analysis by Districts",
            "III. Transaction Analysis by Pincodes"]
        )

        # Question I: State-Level Transactions
        if q == "I. Transaction Analysis by States":
            st.subheader("🌍 Transaction Analysis by States")

            sql_state = """
            SELECT
                states,
                SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
            FROM aggregated_user
            GROUP BY states
            ORDER BY total_value DESC;
            """
            df = pd.read_sql_query(sql_state, engine)

            # Clean state names for GeoJSON
            state_name_map = {
                'Andaman & Nicobar': 'Andaman & Nicobar Islands',
                'Andhra Pradesh': 'Andhra Pradesh',
                'Arunachal Pradesh': 'Arunachal Pradesh',
                'Assam': 'Assam',
                'Bihar': 'Bihar',
                'Chandigarh': 'Chandigarh',
                'Chhattisgarh': 'Chhattisgarh',
                'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
                'Delhi': 'Delhi',
                'Goa': 'Goa',
                'Gujarat': 'Gujarat',
                'Haryana': 'Haryana',
                'Himachal Pradesh': 'Himachal Pradesh',
                'Jammu & Kashmir': 'Jammu and Kashmir',
                'Jharkhand': 'Jharkhand',
                'Karnataka': 'Karnataka',
                'Kerala': 'Kerala',
                'Ladakh': 'Ladakh',
                'Lakshadweep': 'Lakshadweep',
                'Madhya Pradesh': 'Madhya Pradesh',
                'Maharashtra': 'Maharashtra',
                'Manipur': 'Manipur',
                'Meghalaya': 'Meghalaya',
                'Mizoram': 'Mizoram',
                'Nagaland': 'Nagaland',
                'Odisha': 'Odisha',
                'Puducherry': 'Puducherry',
                'Punjab': 'Punjab',
                'Rajasthan': 'Rajasthan',
                'Sikkim': 'Sikkim',
                'Tamil Nadu': 'Tamil Nadu',
                'Telangana': 'Telangana',
                'Tripura': 'Tripura',
                'Uttar Pradesh': 'Uttar Pradesh',
                'Uttarakhand': 'Uttarakhand',
                'West Bengal': 'West Bengal'
            }
            df['state_clean'] = df['states'].map(state_name_map)
            df = df.dropna(subset=['state_clean'])

            # Load India GeoJSON
            geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            resp = requests.get(geojson_url)
            resp.raise_for_status()
            india_geojson = resp.json()

            # Choropleth map
            fig = px.choropleth(
                df,
                geojson=india_geojson,
                featureidkey="properties.ST_NM",
                locations="state_clean",
                color="total_value",
                color_continuous_scale="Blues",
                title="Top States by Transaction Value",
                hover_data={"total_txn": True, "total_value": True}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

        # Question II: District-Level Transactions
        elif q == "II. Transaction Analysis by Districts":
            st.subheader("🏙️ Transaction Analysis by Districts")

            sql_district = """
            SELECT 
                districts, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM map_transaction
            GROUP BY districts 
            ORDER BY total_value DESC
            LIMIT 10;
            """
            query = pd.read_sql_query(sql_district, engine)

            fig = px.bar(
                query,
                x='districts',
                y='total_value',
                title='Top 10 Districts by Transaction Value',
                labels={'total_value': 'Transaction Value (₹)', 'districts': 'District'},
                hover_data=['total_txn']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

        # Question III: Pincode-Level Transactions
        elif q == "III. Transaction Analysis by Pincodes":
            st.subheader("📍 Transaction Analysis by Pincodes")

            sql_pincode = """
            SELECT 
                pincodes, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM top_transaction
            GROUP BY pincodes 
            ORDER BY total_value DESC
            LIMIT 10;
            """
            query = pd.read_sql_query(sql_pincode, engine)

            fig = px.bar(
                query,
                x='pincodes',
                y='total_value',
                title='Top 10 Pincodes by Transaction Value',
                labels={'pincodes': 'Pincode', 'total_value': 'Transaction Value (₹)'},
                hover_data=['total_txn']
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query)

#scenario 4

    elif scenario == "4. User Registration Analysis":
        q = st.selectbox("Choose a Question", [
            "I. User Registration Analysis by Top States",
            "II. User Registration Analysis by Top Districts",
            "III. User Registration Analysis by Top Pincodes"
        ])

        if q == "I. User Registration Analysis by Top States":
            st.subheader("📈 User Registration Analysis by Top States")

            # 1. Year and Quarter selection
            selected_year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023, 2024])
            selected_quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # 2. SQL Query
            q17 = f"""
            SELECT
                states,
                SUM(registered_user) AS total_users
            FROM Map_user 
            WHERE years = '{selected_year}' AND quarter = '{selected_quarter}'
            GROUP BY states
            ORDER BY total_users DESC;
            """
            query = pd.read_sql_query(q17, engine)

            # 3. Corrected state name mapping (matches GeoJSON)
            state_name_map = {
                "Andaman & Nicobar": "Andaman & Nicobar Island",
                "Andhra Pradesh": "Andhra Pradesh",
                "Arunachal Pradesh": "Arunachal Pradesh",
                "Assam": "Assam",
                "Bihar": "Bihar",
                "Chandigarh": "Chandigarh",
                "Chhattisgarh": "Chhattisgarh",
                "Dadra and Nagar Haveli and Daman and Diu": "Dadara & Nagar Havelli",
                "Delhi": "NCT of Delhi",
                "Goa": "Goa",
                "Gujarat": "Gujarat",
                "Haryana": "Haryana",
                "Himachal Pradesh": "Himachal Pradesh",
                "Jammu & Kashmir": "Jammu & Kashmir",
                "Jharkhand": "Jharkhand",
                "Karnataka": "Karnataka",
                "Kerala": "Kerala",
                "Ladakh": "Ladakh",
                "Lakshadweep": "Lakshadweep",
                "Madhya Pradesh": "Madhya Pradesh",
                "Maharashtra": "Maharashtra",
                "Manipur": "Manipur",
                "Meghalaya": "Meghalaya",
                "Mizoram": "Mizoram",
                "Nagaland": "Nagaland",
                "Odisha": "Orissa",
                "Puducherry": "Pondicherry",
                "Punjab": "Punjab",
                "Rajasthan": "Rajasthan",
                "Sikkim": "Sikkim",
                "Tamil Nadu": "Tamil Nadu",
                "Telangana": "Telangana",
                "Tripura": "Tripura",
                "Uttar Pradesh": "Uttar Pradesh",
                "Uttarakhand": "Uttarakhand",
                "West Bengal": "West Bengal"
            }
            query['state_clean'] = query['states'].map(state_name_map)

            # Drop rows without valid mapping
            df = query.dropna(subset=['state_clean'])

            # Identify top 10 states
            top10_states = df.nlargest(10, "total_users")["state_clean"].tolist()

            # Add highlight column (only top 10 states get values, others = 0)
            df["highlight"] = df.apply(
                lambda x: x["total_users"] if x["state_clean"] in top10_states else 0,
                axis=1
            )

            # 4. Load India GeoJSON
            geojson_url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
            resp = requests.get(geojson_url)
            india_geojson = resp.json()

            # 5. Render choropleth (highlight top 10)
            if not df.empty:
                fig = px.choropleth(
                    df,
                    geojson=india_geojson,
                    featureidkey="properties.ST_NM",
                    locations="state_clean",
                    color="highlight",  
                    color_continuous_scale="Blues",
                    title=f"Top 10 States by User Registrations (Year: {selected_year}, Q{selected_quarter})",
                    hover_data={"state_clean": True, "total_users": True}
                )
                fig.update_traces(marker_line_width=0.5, marker_line_color="black")
                fig.update_geos(fitbounds="locations", visible=False)
                fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df[df["state_clean"].isin(top10_states)])
    

        elif q == "II. User Registration Analysis by Top Districts":
            st.subheader("🏙️ User Registration Analysis by Top Districts")

            # Filter selections for year and quarter
            year = st.selectbox("Select Year", [ 2018, 2019, 2020, 2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # SQL Query
            q18 = f"""
            SELECT 
                districts, 
                SUM(registered_user) AS total_users 
            FROM Map_user 
            WHERE years ='{year}'AND quarter = '{quarter}'
            GROUP BY districts 
            ORDER BY total_users DESC ;
            """
            query = pd.read_sql_query(q18,engine)

            st.write(f"✅ Top 10 Districts for {year} Q{quarter}:")


            # Plotly Bar Chart
            fig = px.bar(
                query,
                x='districts',
                y='total_users',
                title=f"Top 10 Districts by Registered Users ({year} Q{quarter})",
                labels={'total_users': 'Registered Users', 'districts': 'District'},
                text='total_users'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query.head(10))

        elif q == "III. User Registration Analysis by Top Pincodes":
            st.subheader("📍 User Registration Analysis by Top Pincodes")

            # Filter selections for year and quarter
            year = st.selectbox("Select Year", [2018,2019,2020,2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # SQL Query
            q19 = f"""
            SELECT 
                Pincodes, 
                SUM(registered_user) AS total_users 
            FROM top_user 
            WHERE years = '{year}' AND quarter = '{quarter}'
            GROUP BY pincodes 
            ORDER BY total_users DESC ;
            """
            query = pd.read_sql_query(q19,engine)

            st.write(f"✅ Top 10 Pincodes for {year} Q{quarter}:")

            # Plotly Bar Chart
            fig = px.bar(
                query,
                x='pincodes',
                y='total_users',
                title=f"Top 10 Pincodes by Registered Users ({year} Q{quarter})",
                labels={'total_users': 'Registered Users', 'pincodes': 'Pincode'},
                text='total_users'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(query.head(10))

             
# Scenario 5

    elif scenario == "5. Insurance Transactions Analysis":
        q = st.selectbox("Choose a Question", [
            "I. Insurance Transactions Analysis Top States",
            "II. Insurance Transactions Analysis by Top Districts",
            "III. Insurance Transactions Analysis by Top Pincodes"
        ])

        if q == "I. Insurance Transactions Analysis Top States":
            st.subheader("🏥 Insurance Transactions Analysis by Top States")

            # 1. Year and Quarter selection
            selected_year = st.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024])
            selected_quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # 2. SQL Query for Insurance Transactions
            q20 = f"""
            SELECT
                States,
                SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
            FROM aggregated_insurance
            WHERE years = '{selected_year}' AND Quarter = '{selected_quarter}'
            GROUP BY States
            ORDER BY Total_value DESC, Total_txn DESC;
            """
            df = pd.read_sql_query(q20,engine)

            # 3. Clean state names
            state_name_map = {
                'Andaman & Nicobar': 'Andaman & Nicobar Islands',
                'Andhra Pradesh': 'Andhra Pradesh',
                'Arunachal Pradesh': 'Arunachal Pradesh',
                'Assam': 'Assam',
                'Bihar': 'Bihar',
                'Chandigarh': 'Chandigarh',
                'Chhattisgarh': 'Chhattisgarh',
                'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
                'Delhi': 'Delhi',
                'Goa': 'Goa',
                'Gujarat': 'Gujarat',
                'Haryana': 'Haryana',
                'Himachal Pradesh': 'Himachal Pradesh',
                'Jammu & Kashmir': 'Jammu and Kashmir',
                'Jharkhand': 'Jharkhand',
                'Karnataka': 'Karnataka',
                'Kerala': 'Kerala',
                'Ladakh': 'Ladakh',
                'Lakshadweep': 'Lakshadweep',
                'Madhya Pradesh': 'Madhya Pradesh',
                'Maharashtra': 'Maharashtra',
                'Manipur': 'Manipur',
                'Meghalaya': 'Meghalaya',
                'Mizoram': 'Mizoram',
                'Nagaland': 'Nagaland',
                'Odisha': 'Odisha',
                'Puducherry': 'Puducherry',
                'Punjab': 'Punjab',
                'Rajasthan': 'Rajasthan',
                'Sikkim': 'Sikkim',
                'Tamil Nadu': 'Tamil Nadu',
                'Telangana': 'Telangana',
                'Tripura': 'Tripura',
                'Uttar Pradesh': 'Uttar Pradesh',
                'Uttarakhand': 'Uttarakhand',
                'West Bengal': 'West Bengal'
            }
            df['state_clean'] = df['states'].map(state_name_map)
            df = df.dropna(subset=['state_clean'])

            # 4. Load GeoJSON for India states
            geojson_url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
            try:
                resp = requests.get(geojson_url)
                resp.raise_for_status()
                india_geojson = resp.json()
            except Exception as e:
                st.error(f"Error loading GeoJSON: {e}")
                st.stop()

            # 5. Render Choropleth Map
            if not df.empty:
                fig = px.choropleth(
                    df,
                    geojson=india_geojson,
                    featureidkey="properties.ST_NM",
                    locations="state_clean",
                    color="total_value",
                    color_continuous_scale="OrRd",
                    title=f"Top 10 States by Insurance Transaction Value ({selected_year}, Q{selected_quarter})",
                    hover_data={"total_txn": True, "total_value": True}
                )
                fig.update_geos(fitbounds="locations", visible=False)
                fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.head(10))
            else:
                st.warning("No data available for the selected year and quarter.")


        elif q == "II. Insurance Transactions Analysis by Top Districts":
            st.subheader("🏥 Insurance Transactions Analysis by Top Districts")

            # Filter selections for year and quarter
            year = st.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # SQL Query
            q21 = f"""
            SELECT 
                districts, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM map_insurance 
            WHERE years = '{year}' AND Quarter = '{quarter}'
            GROUP BY districts 
            ORDER BY total_value DESC, total_txn DESC ;
            """
            query = pd.read_sql_query(q21,engine)

            st.write(f"✅ Top 10 Districts for Insurance Transactions in {year} Q{quarter}:")

            # Plotly Bar Chart
            fig = px.bar(
                query,
                x='districts',
                y='total_value',
                title=f"Top 10 Districts by Insurance Transaction Value ({year} Q{quarter})",
                labels={'total_value': 'Total Transaction Value (₹)', 'districts': 'District'},
                text='total_value'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)

            # Show top 10 table
            st.dataframe(query.head(10))


        elif q == "III. Insurance Transactions Analysis by Top Pincodes":
            st.subheader("🏥 Insurance Transactions Analysis by Top Pincodes")

            # Filter selections for year and quarter
            year = st.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            # Clean SQL Query — no stray spaces
            q22 = f"""
            SELECT 
                pincodes, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM top_insurance
            WHERE years = '{year}' AND Quarter = '{quarter}'
            GROUP BY pincodes 
            ORDER BY total_value DESC, total_txn DESC;
            """

            query = pd.read_sql_query(q22,engine)

            st.write(f"✅ Insurance Transactions for {year} Q{quarter}:")

            if not query.empty:
                # Plotly Bar Chart
                fig = px.bar(
                    query.head(10),  # limit to top 10 in chart
                    x='pincodes',
                    y='total_value',
                    title=f"Top 10 Pincodes by Insurance Transaction Value ({year} Q{quarter})",
                    labels={'total_value': 'Total Transaction Value (₹)', 'pincodes': 'Pincode'},
                    text='total_value'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_tickangle=-45)

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(query.head(10))
            else:
                st.warning(f"No data found for Insurance Transactions in {year} Q{quarter}.")
                st.text("Query preview:")
                st.code(q22, language="sql")



#docs
elif selected == "📄 Docs":
    st.title("📄 Project Documentation")
    st.markdown("""
    ### 📦 Dataset Info
    - **Source:** PhonePe Pulse GitHub (https://github.com/PhonePe/pulse)
    - **Data Format:** JSON
    - **Tools Used for ETL:** Python, Pandas
    - **Database:** PostgreSQL
    - **Visualization:** Plotly, Streamlit
    
    ### 🧩 Tables Used
    - `agg_trans` – Aggregated Transactions
    - `agg_user` – Aggregated User Metrics
    - `map_ins` – Insurance Metrics (District)
    - `top_user` – User by Top Pincodes
    - `top_ins` – Insurance by Top Pincodes

    ### 🧠 SQL Queries Executed
    - State-wise Transaction Aggregation
    - Device Usage Trends
    - Quarterly Growth Comparisons
    - Year-on-Year Trends
    - Top Pincode and District Analysis

    ### 📊 Dashboards Covered
    1. **Decoding Transaction Dynamics on PhonePe**
        -Transaction Dynamics Across States
        -Transaction Dynamics Over Quarters
        -Transaction Dynamics by Payment Category
        -Consistent Growth, Stagnation, or Decline Across States
        -Consistent Growth, Stagnation, or Decline by Transaction Type

    2. **Insurance Engagement Analysis**
        -Insurance Transactions Across States
        -Insurance Transactions Over Quarters
        -Insurance Uptake by Insurance Type
        -Consistent Growth or Decline Across States
        -Consistent Growth or Decline by Insurance Type
                
    3. **Insurance Penetration and Growth Potential Analysis**
        -Insurance Growth Across States
        -Insurance Transactions by Districts",
        -Insurance Transactions by Pincodes"          

    4. **User Registration Analysis**
        - Top states, districts, and pincodes by user registration

    5. **Insurance Transactions Analysis**
        - Insurance transactions by states, districts, and pincodes

    ---

    **📌 Developed by:** Bilk Edison Xavier 
    **📧 Email:** edisonxavier44@gmail.com
    **Linked In : ** https://www.linkedin.com/in/bilk-edison-xavier-1a9767344?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BFw%2BB%2B36mQVWjfPwWwNRa5w%3D%3D
    **GitHub:** https://github.com/BilkEdisonXavier

    ---

    Built with ❤️ using **Python, Pandas, Plotly, Streamlit, PostgreSQL**.
    """)
    
    st.success("Thanks for checking the 📄 Project Documentation!")

#-------------------------------------------------------------------
#Developed By : 

# Bilk Edison Xavier
#email:edisonxavier44@gmail.com
#Github link : https://github.com/BilkEdisonXavier
    
