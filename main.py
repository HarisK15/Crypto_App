from utils import fetch_price
from alerts import check_alert
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--coin", type = str, required= True)
parser.add_argument("--threshold", type = int, required=True)
parser.add_argument("--direction", type = str, required= True, choices=["above", "below"])
args = parser.parse_args()


price = fetch_price(args.coin)





if price is None:
    print(f"❌ Could not fetch price for {args.coin}.")
else:
    message = check_alert(price, args.threshold, args.direction, args.coin)
    print(message)