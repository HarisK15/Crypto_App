import requests
import json

def fetch_price(coin_id):
    Coin = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
    data = Coin.json()
    if coin_id not in data:
        print(f"Coin {coin_id} not found.")
        return None
    return data.get(coin_id).get("usd", None)


def fetch_watchlist(watchlistfile):
    with open(watchlistfile) as f:
        try:
            watchlist = json.load(f)
            return watchlist
        finally:
            f.close()



def fetch_prices_batch(coin_list):
    ids_string = ",".join(coin_list)
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd")
    data = response.json()
    return data
