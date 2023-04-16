import logging

import ccxt
import pandas as pd

log = logging.getLogger(__name__)


class Exchange:
    def __init__(self, exchange_name, config):
        self.exchange_name = exchange_name
        self.config = config
        self.status = "unintiialised"
        self.exchange = None
        self.initialise()

    def initialise(self):
        if self.exchange_name == "bybit":
            self.exchange = ccxt.bybit(
                {
                    "enableRateLimit": True,
                    "apiKey": self.config.api_key,
                    "secret": self.config.api_secret,
                }
            )
            self.status = "initialised"
        else:
            log.warning(f"{self.exchange_name} not implemented yet")

    def setup_exchange(self, symbol):
        values = {"position": False, "margin": False, "leverage": False}
        try:
            self.exchange.set_position_mode(hedged="BothSide", symbol=symbol)
            values["position"] = True
        except Exception as e:
            log.warning(f"An unknown error occurred in with set_position_mode: {e}")
        try:
            self.exchange.set_margin_mode(marginMode="cross", symbol=symbol)
            values["margin"] = True
        except Exception as e:
            log.warning(f"An unknown error occurred in with set_margin_mode: {e}")
        market_data = self.get_market_data(symbol=symbol)
        try:
            self.exchange.set_leverage(leverage=market_data["leverage"], symbol=symbol)
            values["leverage"] = True
        except Exception as e:
            log.warning(f"An unknown error occurred in with set_leverage: {e}")
        log.info(values)

    def get_market_data(self, symbol: str):
        values = {"precision": 0.0, "leverage": 0.0, "min_qty": 0.0}
        try:
            self.exchange.load_markets()
            symbol_data = self.exchange.market(symbol)
            if "info" in symbol_data:
                values["precision"] = symbol_data["info"]["price_scale"]
                values["leverage"] = symbol_data["info"]["leverage_filter"][
                    "max_leverage"
                ]
                values["min_qty"] = symbol_data["info"]["lot_size_filter"][
                    "min_trading_qty"
                ]

        except Exception as e:
            log.warning(f"An unknown error occurred in get_market_data(): {e}")
        return values

    def get_balance(self, quote: str) -> dict:
        values = {
            "available_balance": 0.0,
            "pnl": 0.0,
            "upnl": 0.0,
            "wallet_balance": 0.0,
            "equity": 0.0,
        }
        try:
            data = self.exchange.fetch_balance()
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
            log.warning(f"An unknown error occurred in get_balance(): {e}")
        return values

    def get_orderbook(self, symbol) -> dict:
        values = {"bids": 0.0, "asks": 0.0}
        try:
            data = self.exchange.fetch_order_book(symbol)
            if "bids" in data and "asks" in data:
                if len(data["bids"]) > 0 and len(data["asks"]) > 0:
                    if len(data["bids"][0]) > 0 and len(data["asks"][0]) > 0:
                        values["bids"] = float(data["bids"][0][0])
                        values["asks"] = float(data["asks"][0][0])
        except Exception as e:
            log.warning(f"An unknown error occurred in get_orderbook(): {e}")
        return values

    def get_positions(self, symbol):
        values = {
            "long": {
                "qty": 0.0,
                "price": 0.0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
            "short": {
                "qty": 0.0,
                "price": 0.0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
        }
        try:
            data = self.exchange.fetch_positions([symbol])
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
                    if data[side]["info"]["unrealised_pnl"] is not None:
                        values[sides[side]]["upnl"] = round(
                            float(data[side]["info"]["unrealised_pnl"]), 4
                        )
                    if data[side]["precentage"] is not None:
                        values[sides[side]]["upnl_pct"] = round(
                            float(data[side]["precentage"]), 4
                        )
                    if data[side]["liquidationPrice"] is not None:
                        values[sides[side]]["liq_price"] = float(
                            data[side]["liquidationPrice"]
                        )
                    if data[side]["entryPrice"] is not None:
                        values[sides[side]]["entry_price"] = float(
                            data[side]["entryPrice"]
                        )
        except Exception as e:
            log.warning(f"An unknown error occurred in get_positions(): {e}")
        return values

    def get_current_price(self, symbol):
        current_price = 0.0
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            if "bid" in ticker and "ask" in ticker:
                current_price = (ticker["bid"] + ticker["ask"]) / 2
        except Exception as e:
            log.warning(f"An unknown error occurred in get_positions(): {e}")
        return current_price

    def get_moving_averages(
        self, symbol: str, timeframe: str = "1m", num_bars: int = 20
    ):
        values = {"MA_3_H": 0.0, "MA_3_L": 0.0, "MA_6_H": 0.0, "MA_6_L": 0.0}
        try:
            bars = self.exchange.fetch_ohlcv(
                symbol=symbol, timeframe=timeframe, limit=num_bars
            )
            df = pd.DataFrame(
                bars, columns=["Time", "Open", "High", "Low", "Close", "Volume"]
            )
            df["Time"] = pd.to_datetime(df["Time"], unit="ms")
            df["MA_3_High"] = df.High.rolling(3).mean()
            df["MA_3_Low"] = df.Low.rolling(3).mean()
            df["MA_6_High"] = df.High.rolling(6).mean()
            df["MA_6_Low"] = df.Low.rolling(6).mean()
            values["MA_3_H"] = df["MA_3_High"].iat[-1]
            values["MA_3_L"] = df["MA_3_Low"].iat[-1]
            values["MA_6_H"] = df["MA_6_High"].iat[-1]
            values["MA_6_L"] = df["MA_6_Low"].iat[-1]
        except Exception as e:
            log.warning(f"An unknown error occurred in get_moving_averages(): {e}")
        return values

    def create_limit_order(self, symbol: str, side: str, qty: float, price: float):
        try:
            if side == "buy":
                self.exchange.create_limit_buy_order(
                    symbol=symbol, amount=qty, price=price
                )
            elif side == "sell":
                self.exchange.create_limit_sell_order(
                    symbol=symbol, amount=qty, price=price
                )
            else:
                log.warning(f"side {side} does not exist")
        except Exception as e:
            log.warning(f"An unknown error occurred in create_limit_order(): {e}")
