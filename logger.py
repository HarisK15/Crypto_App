def log_to_file(message:str):
    with open("alerts.log", "a") as file:
        file.write(f"{message}\n")

    with open("alerts.log", "r") as file:
        lines = file.readlines()

    if len(lines)>200:
        with open("alerts.log", "w") as file:
            file.write("-------log cleared------")