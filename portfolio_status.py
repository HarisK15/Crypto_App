import json
import os
import argparse
import csv

from utils import *



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


def write_to_csv(data):
    filename = "portfolio_export.csv"
    if not data:
        print("No data found")
        return
    with open(filename, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("Portfolio exported to CSV")


def prepare_portfolio_data():
    watchlist = fetch_watchlist("watchlist.json")
    data = []

    for item in watchlist:
        coin = item["coin"]
        threshold = item["threshold"]
        direction = item["direction"]
        price = fetch_price(coin)

        data.append({
            "coin": coin,
            "price": price,
            "threshold": threshold,
            "direction": direction
        })

    return data


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("portfolio")
    export_parser = subparsers.add_parser("export")
    args = parser.parse_args()

    if args.command == "portfolio":
        display_portfolio()

    if args.command == "export":
        data = prepare_portfolio_data()
        write_to_csv(data)

if __name__ == "__main__":
    main()