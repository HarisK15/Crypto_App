import requests
import json
import streamlit as st
import time


@st.cache_data(ttl=3000000)
def fetch_price(coin_id):
    # url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    # st.write("fetching price for: ", coin_id)
    # st.write("using url: ", url)
    try:
        Coin = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
        Coin = Coin.strip().lower()
        data = Coin.json()
        if coin_id not in data:
            print(f"Coin {coin_id} not found.")
            return None
        time.sleep(1)
        return data.get(coin_id).get("usd", None)

    except Exception as e:
        return None


def fetch_watchlist(watchlistfile):
    with open(watchlistfile) as f:
        try:
            watchlist = json.load(f)
            return watchlist
        finally:
            f.close()


@st.cache_data(ttl=3000000)
def fetch_prices_batch(coin_list):
    ids_string = ",".join(coin_list)
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd")
    data = response.json()
    return data
