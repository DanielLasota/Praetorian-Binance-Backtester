from pathlib import Path
from typing import Callable

import numpy as np
from cpp_binance_orderbook import OrderBookSessionSimulator, OrderBookMetricsEntry
import pandas as pd

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu


class BacktestSession:

    __slots__ = [
        'callback',
        '_backtest_order_book_metrics_entry_df'
    ]

    def __init__(
            self,
            callback: Callable
    ):
        self.callback: Callable = callback

    def run(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str], save_df: bool = False) -> None:
        self._backtest_loop(list_of_list_of_asset_parameters, variables, save_df)

    def _backtest_loop(self, list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str], save_df: bool = False) -> None:
        dfs: list[pd.DataFrame] = []
        for asset_params in list_of_list_of_asset_parameters:
            csv_name = fu.get_base_of_merged_csv_filename(asset_params)
            csv_path = str(Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv")

            oss = OrderBookSessionSimulator()
            data: dict[str, np.ndarray] = oss.compute_backtest(
                csv_path=csv_path,
                variables=variables,
                python_callback=self._cpp_binance_order_book_witness
            )
            if save_df:
                dfs.append(pd.DataFrame(data))

        if save_df:
            self._backtest_order_book_metrics_entry_df = pd.concat(dfs, ignore_index=True)

    def _cpp_binance_order_book_witness(self, orderbook_entry_metrics: OrderBookMetricsEntry):
        self.callback(orderbook_entry_metrics)

    def get_backtest_order_book_metrics_entry_df(self) -> pd.DataFrame:
        if self._backtest_order_book_metrics_entry_df is None:
            raise RuntimeError("BacktestSession.run(save=True) must be called first")
        return self._backtest_order_book_metrics_entry_df

    def get_final_order_book_metrics_entry(self) -> OrderBookMetricsEntry:
        return self._backtest_order_book_metrics_entry_df.iloc[-1]
