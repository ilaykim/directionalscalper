import logging

from directionalscalper.strategy.strategy import Strategy

log = logging.getLogger(__name__)


class Scalein(Strategy):
    def __init__(self):
        super().__init__()
        self.name = "Scale-in"
        self.version = "0.0.1"

        self.startup_message()
