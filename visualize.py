import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
import matplotlib.dates as mdates


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    plot_parser = subparsers.add_parser("plot")
    plot_parser.add_argument("--coin", type=str, required=True)

    args = parser.parse_args()

    if args.command == "plot":
        plot_price_history(args.coin)


def plot_price_history(coin):
    filename = 'price_history.json'
    try:
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
    except json.JSONDecodeError:
        print("could not decode json")
        return

    filtered_data = [item for item in data if item["coin"].lower() == coin.lower()]
    if not filtered_data:
        print("could not find coin")
        return


    timestamps = []
    prices = []

    for item in filtered_data:
        timestamps.append(item['timestamp'])
        prices.append(item['price'])



    formatted_timestamps = [datetime.fromisoformat(item) for item in timestamps]




    plt.plot(formatted_timestamps, prices, marker='o')
    plt.xlabel('Time')
    plt.ylabel(f"{coin.capitalize()} Price (USD)")
    plt.title(f"{coin.capitalize()} Price History")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    main()




