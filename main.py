from utils import fetch_price
from alerts import check_alert
from utils import fetch_watchlist
import argparse
import time
from utils import fetch_prices_batch
import os
from datetime import datetime
from logger import log_to_file
# parser = argparse.ArgumentParser()
# parser.add_argument("--coin", type = str, required= True)
# parser.add_argument("--threshold", type = int, required=True)
# parser.add_argument("--direction", type = str, required= True, choices=["above", "below"])
# args = parser.parse_args()
#
#
#
# price = fetch_price(args.coin)
#
#
#
#
#
# if price is None:
#     print(f"❌ Could not fetch price for {args.coin}.")
# else:
#     message = check_alert(price, args.threshold, args.direction, args.coin)
#     print(message)

try:
    while True:
        print('Fetching prices...\n')
        watchlist = fetch_watchlist("watchlist.json")

        coin_ids = [item["coin"] for item in watchlist]
        prices = fetch_prices_batch(coin_ids)

        for item in watchlist:
            coin = item["coin"]
            threshold = item["threshold"]
            direction = item["direction"]

            price = prices.get(coin, {}).get("usd")
            if price is None:
                print(f" Could not fetch price for {coin}.")
            else:
                message = check_alert(price, threshold, direction, coin)
                print(message)
                log_to_file(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {message}")

        print("\n waiting 10 minutes...")
        print(f"\n {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Checking crypto prices...\n")
        time.sleep(600)
        os.system('clear')

except KeyboardInterrupt:
    print("\n monitoring stopped by user")


