import logging

log = logging.getLogger(__name__)


class Strategy:
    def __init__(self):
        self.name = None
        self.version = None

    def get_name(self):
        return self.name

    def get_version(self):
        return self.version

    def startup_message(self):
        log.info(f"Loading {self.name} strategy, version {self.version}")
