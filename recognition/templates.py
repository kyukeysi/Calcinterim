SYMBOLS = {
    "0": [],
    "1": [],
    "2": [],
    "3": [],
    "4": [],
    "5": [],
    "6": [],
    "7": [],
    "8": [],
    "9": [],
    "+": [],
    "-": [],
    "×": [],
    "÷": [],
    "x": [],
    "²": [],
    "(": [],
    ")": [],
}


def get_template(symbol):
    return SYMBOLS.get(symbol)


def add_template(symbol, points):
    if symbol not in SYMBOLS:
        raise ValueError(f"Unsupported symbol: {symbol}")

    SYMBOLS[symbol].append(points)