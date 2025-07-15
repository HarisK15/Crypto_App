from utils import fetch_price
from alerts import check_alert
from utils import fetch_watchlist
import argparse
import time
from utils import fetch_prices_batch
import os
from datetime import datetime
from logger import log_to_file
from notifier import send_email_alert


try:
    while True:
        print('Fetching prices...\n')
        watchlist = fetch_watchlist("watchlist.json")

        coin_ids = [item["coin"] for item in watchlist]
        prices = fetch_prices_batch(coin_ids)

        alerts = []

        for item in watchlist:
            coin = item["coin"]
            threshold = item["threshold"]
            direction = item["direction"]

            price = prices.get(coin, {}).get("usd")
            if price is None:
                print(f" Could not fetch price for {coin}.")
            else:
                message = check_alert(price, threshold, direction, coin)
                alerts.append(message)
                print(message)
                log_to_file(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {message}")

        if alerts:
            combined_message = "\n".join(alerts)
            send_email_alert("cryptoproject543@gmail.com", "Crypto Price Alerts", combined_message)

        print("\n waiting 10 minutes...")
        print(f"\n {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Checking crypto prices...\n")
        time.sleep(600)
        os.system('clear')

except KeyboardInterrupt:
    print("\n monitoring stopped by user")


