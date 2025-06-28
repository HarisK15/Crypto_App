def check_alert(price, threshold, direction, coin):
    if direction == "above":
        if price > threshold:
            return f"Alert!!! {coin} is above threshold of {threshold}, current value is {price}"
        else:
            return f"No alert. {coin} is still below threshold of {threshold}, current value is {price}"

    elif direction == "below":
        if price < threshold:
            return f"Alert!!! {coin} is below threshold of {threshold}"
        else:
            return f"No alert. {coin} is still above threshold of {threshold}, current value is {price}"

