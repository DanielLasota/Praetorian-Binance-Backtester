from operator import attrgetter
from pathlib import Path
from typing import Callable
from alive_progress import alive_bar
from cpp_binance_orderbook import OrderBookSessionSimulator, OrderBookMetricsEntry
import pandas as pd

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.utils.colors import Colors
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu
from praetorian_binance_backtester.utils.time_utils import measure_time


class BacktestSession:

    __slots__ = [
        'callback',
        '_backtest_entry_list'
    ]

    def __init__(
            self,
            callback: Callable
    ):
        self.callback: Callable = callback
        self._backtest_entry_list = []

    def run(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str]) -> None:
        self._backtest_loop(list_of_list_of_asset_parameters, variables)

    @measure_time
    def _backtest_loop(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str]) -> None:
        print(Colors.CYAN)
        with alive_bar(len(list_of_list_of_asset_parameters), title='Backtest Session', spinner='dots_waves', force_tty=False) as bar:
            for list_of_asset_parameters in list_of_list_of_asset_parameters:
                csv_name = fu.get_base_of_merged_csv_filename(list_of_asset_parameters)
                csv_path = str(Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv")

                oss = OrderBookSessionSimulator()
                list_of_order_book_metrics_entry = oss.compute_backtest(
                    csv_path=csv_path,
                    variables=variables,
                    python_callback=self._cpp_binance_order_book_witness
                )
                self._backtest_entry_list.extend(list_of_order_book_metrics_entry)
                bar()
        print(Colors.RESET)

    def _cpp_binance_order_book_witness(self, orderbook_entry_metrics: OrderBookMetricsEntry):
        self.callback(orderbook_entry_metrics)

    @measure_time
    def get_backtest_order_book_metrics_entry_df(self, variables: list[str]) -> pd.DataFrame:
        getters = {var: attrgetter(var) for var in variables}
        data = {var: [] for var in variables}

        for entry in self._backtest_entry_list:
            for var, getter in getters.items():
                data[var].append(getter(entry))

        return pd.DataFrame(data)

    def get_final_order_book_metrics_entry(self) -> OrderBookMetricsEntry:
        return self._backtest_entry_list[-1]
