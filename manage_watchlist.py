import json
import argparse
import os


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add")
add_parser.add_argument("--coin", type=str, required=True)
add_parser.add_argument("--threshold", type=int, required=True)
add_parser.add_argument("--direction", type=str, required=True, choices=["above", "below"])

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("--coin", type=str, required=True)

show_parser = subparsers.add_parser("show")

args = parser.parse_args()

def add_to_watchlist(coin, threshold, direction):
    filename = "watchlist.json"
    data = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON root must be in list")
            except ValueError:
                pass
    for item in data:
        if item["coin"] == coin and item["threshold"] == threshold and item["direction"] == direction:
            print(f"alert is already in the watchlist")
            return


    new_dict = {"coin": coin, "threshold": threshold, "direction": direction}
    data.append(new_dict)
    with open(filename, 'w') as f:
        json.dump(data, f,indent=4)
        print(f"Added {coin} to watchlist")





#
def remove_from_watchlist(coin):
    filename = "watchlist.json"
    data = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON root must be in list")
            except ValueError:
                pass
    original_length = len(data)
    filtered_data = [item for item in data if item["coin"] != coin]
    if len(filtered_data) == original_length:
        print("nothing removed")
    else:
        with open(filename, 'w') as f:
            json.dump(filtered_data, f,indent=4)
        print(f"Removed {coin} from watchlist")




def show_watchlist():
    try:
        filename = "watchlist.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                if not data:
                    print("No data found")
                else:
                    print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print("No watchlist found")



if args.command == "add":
    add_to_watchlist(args.coin, args.threshold, args.direction)
elif args.command == "remove":
    remove_from_watchlist(args.coin)
elif args.command == "show":
    show_watchlist()