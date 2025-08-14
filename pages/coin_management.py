import streamlit as st
from database import db_manager, get_watchlist
from utils import fetch_prices_batch, validate_coin_id
from datetime import datetime

st.title("🪙 Coin Management")

# Get the current watchlist from the database
watchlist = get_watchlist()

if watchlist:
    st.subheader("📋 Current Watchlist")
    
    # Show each coin in the watchlist
    for item in watchlist:
        coin_id = item["coin_id"]
        coin_name = item["coin_name"]
        threshold_above = item.get("threshold_above")
        threshold_below = item.get("threshold_below")
        
        # Layout for displaying coin info
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.write(f"**{coin_name.title()}**")
        
        with col2:
            if threshold_above:
                st.write(f"Alert above: ${threshold_above:,.2f}")
            else:
                st.write("No upper threshold")
        
        with col3:
            if threshold_below:
                st.write(f"Alert below: ${threshold_below:,.2f}")
            else:
                st.write("No lower threshold")
        
        with col4:
            if st.button("Remove", key=f"remove_{coin_id}"):
                if db_manager.remove_from_watchlist(coin_id):
                    st.success(f"Removed {coin_name}")
                    st.rerun()
                else:
                    st.error("Failed to remove coin")
        
        st.divider()
else:
    st.info("No coins in watchlist yet. Add some coins below!")

# Form for adding new coins
st.subheader("➕ Add New Coin")
with st.form("add_form"):
    coin_id = st.text_input("Coin ID (e.g., bitcoin)", key="add_coin_id")
    threshold_above = st.number_input("Alert Above ($)", min_value=0.0, step=0.01, key="add_threshold_above")
    threshold_below = st.number_input("Alert Below ($)", min_value=0.0, step=0.01, key="add_threshold_below")
    
    submitted = st.form_submit_button("Add Coin")
    
    if submitted:
        if coin_id and validate_coin_id(coin_id):
            # Check if the coin exists by trying to get its price
            price_data = fetch_prices_batch([coin_id])
            if coin_id in price_data:
                coin_name = coin_id.title()
                if db_manager.add_to_watchlist(
                    coin_id, coin_name, threshold_above, threshold_below
                ):
                    st.success(f"Added {coin_name} to watchlist")
                    st.rerun()
                else:
                    st.error("Failed to add coin to watchlist")
            else:
                st.error(f"Coin {coin_id} not found. Please check the coin ID.")
        else:
            st.error("Invalid coin ID. Please use lowercase letters and hyphens only.")

# Show when we last refreshed
st.write("Last refreshed at:", datetime.now().strftime("%H:%M:%S"))

# Button to refresh the data
if st.button("🔄 Refresh Data", key="refresh_data"):
    st.rerun()