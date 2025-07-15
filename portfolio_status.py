import json
import os
import argparse

from utils import *

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("portfolio")
    args = parser.parse_args()

    if args.command == "portfolio":
        display_portfolio()

def display_portfolio():
    filename = "watchlist.json"
    if not os.path.isfile(filename):
        print("No watchlist.json file")
        return
    with open(filename) as json_file:
        data = json.load(json_file)
        for item in data:
            coin = item["coin"]
            price = fetch_price(coin)
            threshold = item["threshold"]
            direction = item["direction"]

            status = 'alert triggered'


            if ((price > threshold and direction == "above") or (price < threshold and direction == "below")):
                print(status)
            else:
                print("no alert")
            print(f"{coin.capitalize()}: ${price} (threshold: {threshold}, direction: {direction}) → {status}")




if __name__ == "__main__":
    main()