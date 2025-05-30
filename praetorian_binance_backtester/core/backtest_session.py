from pathlib import Path
from typing import Callable

from cpp_binance_orderbook import OrderBookSessionSimulator

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu


class BacktestSession:

    def __init__(self):
        ...

    @staticmethod
    def run(list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str], python_callback: Callable) -> None:
        BacktestSession._backtest_loop(list_of_list_of_asset_parameters, variables, python_callback)

    @staticmethod
    def _backtest_loop(list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list[str], python_callback: Callable) -> None:
        for list_of_asset_parameters in list_of_list_of_asset_parameters:
            csv_name = fu.get_base_of_merged_csv_filename(list_of_asset_parameters)
            csv_path = str(Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv")

            oss = OrderBookSessionSimulator()
            oss.compute_backtest(
                csv_path=csv_path,
                variables=variables,
                python_callback=python_callback
            )
