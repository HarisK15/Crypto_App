
def check_alert(price, threshold, direction, coin):
    if direction == "above":
        if price > threshold:
            message = f"Alert!!! {coin} is above threshold of {threshold}, current value is {price}"
            return message

        else:
            return f"No alert. {coin} is still below threshold of {threshold}, current value is {price}"

    elif direction == "below":
        if price < threshold:
            message = f"Alert!!! {coin} is below threshold of {threshold}"
            return message

        else:
            return f"No alert. {coin} is still above threshold of {threshold}, current value is {price}"

