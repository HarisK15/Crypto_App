import streamlit as st
from app import add_to_watchlist
from app import remove_from_watchlist
from datetime import datetime
import json
from utils import fetch_price
import os


st.title("Coin Management")



watchlist_file = "watchlist.json"
if os.path.exists(watchlist_file):
    with open(watchlist_file, "r") as f:
        watchlist = json.load(f)
else:
    watchlist = []



for item in watchlist:
    coin = item["coin"]
    threshold = item["threshold"]
    direction = item["direction"]
    price = fetch_price(coin)
    # st.metric(label=f"{coin.capitalize()} price", value=f"${price}")
    # st.caption(f"Alert when {direction} {threshold}")
    # st.write(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd")
coin_names = list(set([item["coin"].lower() for item in watchlist]))


st.subheader("➕ Add New Coin")
with st.form("add_form"):
    coin = st.text_input("Coin ID (e.g., bitcoin)")
    threshold = st.number_input("Threshold", step=1.0)
    direction = st.selectbox("Direction", ["above", "below"])
    submitted = st.form_submit_button("Add")
    if submitted:
        add_to_watchlist(coin, threshold, direction)
        st.success(f"Added {coin} to watchlist")


st.subheader("❌ Remove Coin")
with st.form("remove_form"):
    coin_to_remove = st.selectbox("Coin to remove", coin_names)
    removed = st.form_submit_button("Remove")
    if removed:
        remove_from_watchlist(coin_to_remove)
        st.success(f"Removed {coin_to_remove} from watchlist")

st.write("Last refreshed at:", datetime.now().strftime("%H:%M:%S"))