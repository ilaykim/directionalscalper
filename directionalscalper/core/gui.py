import logging

from rich.table import Table

from directionalscalper.core.functions import calc_lot_size

log = logging.getLogger(__name__)


class GUI:
    def __init__(self, api, config, version):
        self.api = api
        self.config = config
        self.version = version

    def create_table(self, **kwargs):
        table = Table(show_header=False, box=None, title=self.version)
        return table
