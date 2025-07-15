from datetime import datetime
from os import close

import requests
import json
import os

def log_to_file(message:str):
    with open("alerts.log", "a") as file:
        file.write(f"{message}\n")

    with open("alerts.log", "r") as file:
        lines = file.readlines()

    if len(lines)>50:
        with open("alerts.log", "w") as file:
            file.write("-------log cleared------")


def log_price_history(price, coin):
    entry = {
        "coin": coin,
        "timestamp": datetime.now().isoformat(),
        "price": price
    }
    filename = "price_history.json"
    try:
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                data = json.load(file)
        else:
            data = []
    except json.JSONDecodeError:
        data = []

    data.append(entry)

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)







