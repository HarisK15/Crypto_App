import requests


def fetch_price(coin_id):
    Coin = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
    data = Coin.json()
    return data.get(coin_id).get("usd", None)