import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from colorama import Fore, Style
from rich.live import Live

sys.path.append(".")
from directionalscalper.api.manager import Manager
from directionalscalper.core import tables
from directionalscalper.core.config import load_config
from directionalscalper.core.exchange import Exchange
from directionalscalper.core.functions import print_lot_sizes
from directionalscalper.core.logger import Logger
from directionalscalper.messengers.manager import MessageManager


class Bot:
    def __init__(self, api, exchange, config):
        self.api = api
        self.exchange = exchange
        self.config = config
        self.version = "1.1.7"

        self.quote = "USDT"
        self.run()

    def run(self):
        balance = self.exchange.get_balance(quote=self.quote)
        ob = self.exchange.get_orderbook(symbol=self.config.symbol)
        positions = self.exchange.get_positions(symbol=self.config.symbol)
        log.info(balance)
        log.info(ob)
        log.info(positions)


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

    exchange = Exchange(exchange_name=config.exchange.name, config=config.exchange)

    bot = Bot(exchange=exchange, api=manager, config=config.bot)
