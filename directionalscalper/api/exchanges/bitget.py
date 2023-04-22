from __future__ import annotations

import logging

from directionalscalper.api.exchanges.exchange import Exchange
from directionalscalper.api.exchanges.utils import Intervals
from directionalscalper.core.utils import send_public_request, send_signed_request

log = logging.getLogger(__name__)


class Bitget(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Bitget initialised")

    exchange = "bitget"
    futures_api_url = "https://api.bitget.com"
    max_weight = 1000

    def get_futures_symbols(self) -> dict:
        self.check_weight()
        symbols_list = {}
        params: dict = {"productType": "umcbl"}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/api/mix/v1/market/contracts",
            payload=params,
        )
        leverages = self.get_max_leverages()
        if "data" in raw_json:
            for symbol in raw_json["data"]:
                if symbol["symbolStatus"] == "normal":
                    tick_size, min_quantity, qty_step = (
                        float(0),
                        float(0),
                        float(0),
                    )
                    leverage = 0
                    if leverages:
                        if symbol in leverages:
                            leverage = leverages[symbol]

                    symbols_list[symbol["symbol"]] = {
                        "launch": 0,
                        "price_scale": 1 / 10 ** float(symbol["pricePlace"]),
                        "max_leverage": leverage,
                        "tick_size": tick_size,
                        "min_order_qty": min_quantity,
                        "qty_step": qty_step,
                    }
        return symbols_list

    def get_max_leverages(self) -> dict:  # requires authentication
        params: dict = {"productType": "umcbl"}
        header, raw_json = send_signed_request(
            base_url=self.futures_api_url,
            http_method="GET",
            url_path="/api/mix/v1/market/contracts",
            payload=params,
        )
        leverages = {}
        if "data" in raw_json:
            for symbol in raw_json["data"]:
                leverages[symbol] = self.get_max_leverage(symbol=symbol)
        return leverages

    def get_max_leverage(self, symbol: str) -> float:
        params: dict = {"symbol": symbol.upper()}
        header, raw_json = send_signed_request(
            base_url=self.futures_api_url,
            http_method="GET",
            url_path="/api/mix/v1/market/symbol-leverage",
            payload=params,
        )
        leverage = 0.0
        if "data" in raw_json:
            if "maxLeverage" in raw_json["data"]:
                return float(raw_json["data"]["maxLeverage"])
        return leverage

    def get_futures_price(self, symbol: str) -> float:
        self.check_weight()
        params = {"symbol": symbol.upper()}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/api/mix/v1/market/tickers",
            payload=params,
        )

        if "data" in raw_json:
            if "last" in raw_json["data"]:
                return float(raw_json["data"]["last"])
        return float(-1.0)

    def get_futures_prices(self) -> dict:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/api/mix/v1/market/tickers",
            payload=params,
        )
        prices = {}
        if "data" in raw_json:
            for pair in raw_json["data"]:
                prices[pair["symbol"]] = float(pair["last"])
        return prices

    def get_futures_volumes(self) -> dict:
        self.check_weight()

        volumes: dict = {}

        return volumes

    def get_futures_kline(
        self,
        symbol: str,
        interval: Intervals = Intervals.ONE_DAY,
        limit: int = 200,
    ) -> list:
        self.check_weight()

        params = {"symbol": symbol.upper(), "limit": limit, "granularity": interval}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/fapi/v1/klines",
            payload=params,
        )

        if len(raw_json) > 0:
            return [
                {
                    "timestamp": int(candle[0]),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                }
                for candle in raw_json
            ]
        return []

    def get_funding_rate(self, symbol: str) -> float:
        self.check_weight()
        params = {"symbol": symbol.upper()}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/api/mix/v1/market/current-fundRate",
            payload=params,
        )
        if "data" in raw_json:
            if "fundingRate" in raw_json["data"]:
                return float(raw_json["data"]["fundingRate"])
        return 0.0

    def get_open_interest(
        self, symbol: str, interval: Intervals = Intervals.ONE_DAY, limit: int = 200
    ) -> list:
        self.check_weight()
        oi: list = []
        params = {"symbol": symbol.upper()}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/api/mix/v1/market/open-interest",
            payload=params,
        )
        if "data" in raw_json:
            if "amount" in raw_json["data"]:
                return [float(raw_json["data"]["amount"])]
        return oi
