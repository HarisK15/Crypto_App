import streamlit as st
from utils import fetch_price
from manage_watchlist import add_to_watchlist, remove_from_watchlist
from visualize import plot_price_history
import json
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt
from utils import fetch_prices_batch

default_watchlist = [
    {"coin": "bitcoin", "threshold": 100000, "direction": "above"},
    {"coin": "ethereum", "threshold": 3000, "direction": "above"},
    {"coin": "solana", "threshold": 200, "direction": "below"}
]

@st.cache_data(ttl=300)
def get_price_history_df(coin):
    filename = "price_history.json"
    if not os.path.exists(filename):
        return pd.DataFrame()

    try:
        with open(filename, "r") as f:
            data = json.load(f)
            coin_data = [
                {
                    "timestamp": datetime.fromisoformat(entry["timestamp"]),
                    "price": entry["price"]
                }
                for entry in data if entry["coin"] == coin
            ]
            df = pd.DataFrame(coin_data)
            return df.sort_values("timestamp")
    except json.JSONDecodeError:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_price_history(coin):
    filename = "price_history.json"
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            coin_data = [
                {
                "timestamp": entry["timestamp"],
                "price": entry["price"]
                }
                for entry in data if entry["coin"] == coin
            ]
            if not coin_data:
                return None
            df = pd.DataFrame(coin_data)
            return df
    except json.JSONDecodeError:
        return None


def main():


    st.title("📈 Crypto Watchlist Dashboard")
    # st_autorefresh(interval=60000, key="datarefresh")

    # 2. Load Watchlist
    watchlist_file = "watchlist.json"
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r") as f:
            watchlist = json.load(f)
    else:
        watchlist = default_watchlist
        with open(watchlist_file, "w") as f:
            json.dump(watchlist, f, indent=4)
    coin_names = list(set(item["coin"] for item in watchlist))
    price_data = fetch_prices_batch(coin_names)


    st.subheader("🔍 Current Prices")
    for item in watchlist:
        coin = item["coin"]
        threshold = item["threshold"]
        direction = item["direction"]
        price = price_data.get(coin, {}).get("usd")
        st.metric(label=f"{coin.capitalize()} price", value=f"${price}" if price else "N/A")
        st.caption(f"Alert when {direction} {threshold}")


    st.subheader("📊 Price History Viewer")

    coin_names = list(set([item["coin"].lower() for item in watchlist]))




    if coin_names:
        selected_coin = st.selectbox("Select a coin", sorted(coin_names))

        if selected_coin:
            price = price_data.get(selected_coin, {}).get("usd")
            if price:
                st.metric(label=f"{selected_coin.capitalize()} price", value=f"${price}")
            else:
                st.error(f"{selected_coin.capitalize()} Coin not found")

            df = get_price_history_df(selected_coin)
            if not df.empty:
                st.line_chart(df.set_index("timestamp"))
            else:
                st.info("No price history available for this coin.")

            plt.figure(figsize=(10, 4))
            # plt.plot(df["timestamp"], df["price"], marker='o')
            # plt.xlabel("Time")
            # plt.ylabel(f"{selected_coin.capitalize()} price (USD)")
            # plt.title(f"{selected_coin.capitalize()} price History")
            # plt.grid(True)
            # plt.xticks(rotation=45)
            # plt.tight_layout()
            # st.pyplot(plt)

            df = get_price_history(selected_coin)
            if df is not None:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="⬇️ Download Price History as CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"{selected_coin}_price_history.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No price history available for CSV export.")

    else:
        st.write("no coins in watchlist")














if __name__ == "__main__":
    main()


