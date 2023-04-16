import argparse
import sys
import time
import os
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
from directionalscalper.strategy.aggressive import Aggressive
from directionalscalper.strategy.blackjack import Blackjack
from directionalscalper.strategy.hedge import Hedge
from directionalscalper.strategy.long import Long
from directionalscalper.strategy.scalein import Scalein
from directionalscalper.strategy.short import Short
from directionalscalper.strategy.violent import Violent

class Bot:
    def __init__(self, api, exchange, config, strategy):
        self.api = api
        self.exchange = exchange
        self.config = config
        self.strategy = strategy
        self.version = "1.1.7"

        self.startup_message()

        if self.exchange is not None and self.config is not None:
            self.quote = "USDT"
            self.exchange.setup_exchange(symbol=self.config.symbol)
            self.run()
        else:
            log.error("Unable to start the bot without a valid configuration.")

    def run(self):
        balance = self.exchange.get_balance(quote=self.quote)
        ob = self.exchange.get_orderbook(symbol=self.config.symbol)
        positions = self.exchange.get_positions(symbol=self.config.symbol)
        log.info(balance)
        log.info(ob)
        log.info(positions)

    def startup_message(self):
        log.info(f"Loading {self.strategy.get_name()} strategy, version {self.strategy.get_version()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Directional Scalper Bot")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--strategy", default="hedge", help="Trading strategy")
    args = parser.parse_args()

    config_file = args.config
    config_file_path = Path(Path().resolve(), "config", config_file)
    strategy_name = args.strategy.lower()

    # Check if config file exists
    if not config_file_path.exists():
        print(f"Error: Configuration file '{config_file_path}' does not exist.")
        exit(1)

    config = load_config(path=config_file_path)
    log = Logger(filename="ds.log", level=config.logger.level)

    # Check for a valid strategy
    strategy_map = {
        "aggressive": Aggressive,
        "blackjack": Blackjack,
        "hedge": Hedge,
        "long": Long,
        "scalein": Scalein,
        "short": Short,
        "violent": Violent,
    }

    if strategy_name in strategy_map:
        strategy = strategy_map[strategy_name]()
    else:
        log.error(f"Invalid strategy: {strategy_name}. Please choose a valid strategy.")
        exit(1)

    manager = Manager(
        api=config.api.mode,
        path=Path("data", config.api.filename),
        url=f"{config.api.url}{config.api.filename}",
    )

    exchange = Exchange(exchange_name=config.exchange.name, config=config.exchange)
    bot = Bot(exchange=exchange, api=manager, config=config.bot, strategy=strategy)
