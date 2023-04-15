import argparse
import sys
import time
from pathlib import Path

import ccxt
import pandas as pd
from colorama import Fore, Style
from rich.live import Live

sys.path.append(".")
from directionalscalper.api.manager import Manager
from directionalscalper.core import tables
from directionalscalper.core.config import load_config
from directionalscalper.core.functions import print_lot_sizes
from directionalscalper.core.logger import Logger
from directionalscalper.messengers.manager import MessageManager


class Bot:
    def __init__(self, api, exchange):
        self.api = api
        self.exchange = exchange
        self.version = "1.1.7"

    def get_balance(self, quote: str) -> dict:
        values = {
            "available_balance": 0.0,
            "pnl": 0.0,
            "upnl": 0.0,
            "wallet_balance": 0.0,
            "equity": 0.0,
        }
        try:
            data = exchange.fetch_balance()
            if "info" in data:
                if "result" in data["info"]:
                    if quote in data["info"]["result"]:
                        values["available_balance"] = float(
                            data["info"]["result"][quote]["available_balance"]
                        )
                        values["pnl"] = float(
                            data["info"]["result"][quote]["realised_pnl"]
                        )
                        values["upnl"] = float(
                            data["info"]["result"][quote]["unrealised_pnl"]
                        )
                        values["wallet_balance"] = round(
                            float(data["info"]["result"][quote]["wallet_balance"]), 2
                        )
                        values["equity"] = round(
                            float(data["info"]["result"][quote]["equity"]), 2
                        )
        except Exception as e:
            print(f"An unknown error occured in get_balance(): {e}")
            log.warning(f"{e}")
        return values

    def get_orderbook(self, symbol) -> dict:
        values = {"bids": 0, "asks": 0}
        try:
            data = exchange.fetch_order_book(symbol)
            if "bids" in data and "asks" in data:
                if len(data["bids"]) > 0 and len(data["asks"]) > 0:
                    if len(data["bids"][0]) > 0 and len(data["asks"][0]) > 0:
                        values["bids"] = int(data["bids"][0][0])
                        values["asks"] = int(data["asks"][0][0])
        except Exception as e:
            print(f"An unknown error occured in get_orderbook(): {e}")
            log.warning(f"{e}")
        return values

    def get_positions(self, symbol):
        values = {
            "long": {
                "qty": 0,
                "price": 0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
            "short": {
                "qty": 0,
                "price": 0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
        }
        try:
            data = exchange.fetch_positions([symbol])
            if len(data) == 2:
                sides = ["long", "short"]
                for side in [0, 1]:
                    values[sides[side]]["qty"] = float(data[side]["contracts"])
                    values[sides[side]]["price"] = float(data[side]["entryPrice"])
                    values[sides[side]]["realised"] = round(
                        float(data[side]["info"]["realised_pnl"]), 4
                    )
                    values[sides[side]]["cum_realised"] = round(
                        float(data[side]["info"]["cum_realised_pnl"]), 4
                    )
                    values[sides[side]]["upnl"] = round(
                        float(data[side]["info"]["unrealised_pnl"]), 4
                    )
                    values[sides[side]]["upnl_pct"] = round(
                        float(data[side]["precentage"]), 4
                    )
                    values[sides[side]]["liq_price"] = float(
                        data[side]["liquidationPrice"]
                    )
                    values[sides[side]]["entry_price"] = float(data[side]["entryPrice"])
        except Exception as e:
            print(f"An unknown error occured in get_orderbook(): {e}")
            log.warning(f"{e}")
        return values


if __name__ == "__main__":
    config_file = "config.json"
    config_file_path = Path(Path().resolve(), "config", config_file)
    config = load_config(path=config_file_path)

    log = Logger(filename="ds.log", level=config.logger.level)

    manager = Manager(
        api=config.api.mode,
        path=Path("data", config.api.filename),
        url=f"{config.api.url}{config.api.filename}",
    )

    exchange = ccxt.bybit(
        {
            "enableRateLimit": True,
            "apiKey": config.exchange.api_key,
            "secret": config.exchange.api_secret,
        }
    )

    bot = Bot(exchange=exchange, api=manager)
