from pathlib import Path
from typing import Callable
from cpp_binance_orderbook import OrderBookSessionSimulator, OrderBookMetricsEntry
import pandas as pd

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu


class BacktestSession:

    __slots__ = [
        'callback',
        '_backtest_entry_list',
    ]

    def __init__(
            self,
            callback: Callable
    ):
        self.callback: Callable = callback
        self._backtest_entry_list = []

    def run(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str]) -> None:
        self._backtest_loop(list_of_list_of_asset_parameters, variables)

    def _backtest_loop(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str]) -> None:
        for list_of_asset_parameters in list_of_list_of_asset_parameters:
            csv_name = fu.get_base_of_merged_csv_filename(list_of_asset_parameters)
            csv_path = str(Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv")

            oss = OrderBookSessionSimulator()
            oss.compute_backtest(
                csv_path=csv_path,
                variables=variables,
                python_callback=self._cpp_binance_order_book_witness
            )

    def _cpp_binance_order_book_witness(self, orderbook_entry_metrics: OrderBookMetricsEntry):
        self._backtest_entry_list.append(orderbook_entry_metrics)
        self.callback(orderbook_entry_metrics)

    def get_backtest_entry_df(self, variables: list[str]) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {var: getattr(entry, var) for var in variables}
                for entry in self._backtest_entry_list
            ]
        )

    def get_final_order_book_metrics_entry(self) -> OrderBookMetricsEntry:
        return self._backtest_entry_list[-1]
