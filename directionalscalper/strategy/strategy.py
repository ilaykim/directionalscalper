import logging

log = logging.getLogger(__name__)


class Strategy:
    def __init__(self):
        self.name = "Not loaded"
        self.version = "0.0.0"

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.version

    def startup_message(self):
        log.info(f"Loading {self.name} strategy, version {self.version}")

    def position_entry(self):
        pass

    def position_exit(self):
        pass

    def check_orders(self):
        pass
