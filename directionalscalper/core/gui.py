import logging

from rich.table import Table

from directionalscalper.core.functions import calc_lot_size

log = logging.getLogger(__name__)


class GUI:
    def __init__(self, api, config, version):
        self.api = api
        self.config = config
        self.version = version

    def create_table(self, data: dict):
        table = Table(show_header=False, box=None, title=self.version)
        table.add_row(self.create_table_info(data=data))
        return table

    def create_table_info(self, data: dict):
        table = Table(show_header=False, width=50)
        table.add_column(justify="right")
        table.add_column(justify="left")
        table_order = ["symbol", "balance", "equity"]
        formatted = ["balance", "equity"]
        for item in table_order:
            if item in data:
                if item in formatted:
                    table.add_row(item.title(), f"${data[item]:.2f}")
                else:
                    table.add_row(item.title(), f"{data[item]}")

        return table
