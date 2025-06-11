from operator import attrgetter

import numpy as np
import pandas as pd
from pathlib import Path
from alive_progress import alive_bar
from cpp_binance_orderbook import OrderBookSessionSimulator, OrderBookMetricsEntry

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.enums.backtester_config import LEARNING_PROCESS_AMOUNT
from praetorian_binance_backtester.utils.colors import Colors
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu
from praetorian_binance_backtester.utils.time_utils import measure_time


class LearnSession:

    __slots__ = []

    @staticmethod
    @measure_time
    def compute_variables_df(list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list) -> pd.DataFrame:
        if LEARNING_PROCESS_AMOUNT == 1:
            return LearnSession._date_range_single_process_iterator(list_of_list_of_asset_parameters, variables)
        else:
            return LearnSession._date_range_multiprocessing_iterator(list_of_list_of_asset_parameters, variables)

    @staticmethod
    def _date_range_single_process_iterator(list_of_list_of_asset_parameters: list[list[AssetParameters]], variables: list) -> pd.DataFrame:
        dataframes = []
        print(Colors.CYAN)
        with alive_bar(len(list_of_list_of_asset_parameters), title='Learn Session', spinner='dots_waves') as bar:
            for list_of_asset_parameters in list_of_list_of_asset_parameters:
                df = LearnSession._compute_variables_for_single_merged_csv(list_of_asset_parameters, variables)
                dataframes.append(df)
                bar()
        print(Colors.RESET)
        return pd.concat(dataframes, ignore_index=True)

    @staticmethod
    def _date_range_multiprocessing_iterator(list_of_list_of_asset_parameters, variables) -> pd.DataFrame:
        import multiprocessing
        print(Colors.CYAN)
        with alive_bar(len(list_of_list_of_asset_parameters), title=f'Learn Session', spinner='dots_waves') as bar:
            with multiprocessing.Pool(processes=LEARNING_PROCESS_AMOUNT) as pool:
                dfs = pool.starmap(
                    LearnSession._compute_variables_for_single_merged_csv,
                    [(list_of_asset_parameters, variables) for list_of_asset_parameters in list_of_list_of_asset_parameters]
                )
                bar(len(list_of_list_of_asset_parameters))
        print(Colors.RESET)
        return pd.concat(dfs, ignore_index=True)

    @staticmethod
    @measure_time
    def _compute_variables_for_single_merged_csv(list_of_asset_parameters: list[AssetParameters], variables: list) -> pd.DataFrame:
        csv_name = fu.get_base_of_merged_csv_filename(list_of_asset_parameters)
        csv_path = str(Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv")

        oss = OrderBookSessionSimulator()
        data: dict[str, np.ndarray] = oss.compute_variables_numpy(csv_path, variables)
        return pd.DataFrame(data)

    @staticmethod
    @measure_time
    def _convert_order_book_metrics_entry_list_to_df(
            orderbook_metrics_entries: list[OrderBookMetricsEntry],
            variables: list[str]
    ) -> pd.DataFrame:
        getters = {var: attrgetter(var) for var in variables}
        data = {var: [] for var in variables}

        for entry in orderbook_metrics_entries:
            for var, getter in getters.items():
                data[var].append(getter(entry))

        return pd.DataFrame(data)
