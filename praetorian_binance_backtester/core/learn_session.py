import pandas as pd
from pathlib import Path
from cpp_binance_orderbook import OrderBookSessionSimulator

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.backtester_config import MERGED_CSVS_NEST_CATALOG
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu

class LearnSession:

    @staticmethod
    def learn(list_of_list_of_asset_parameters: list[list[AssetParameters]], variable_list: list) -> pd.DataFrame:
        return LearnSession._date_range_iterator(list_of_list_of_asset_parameters, variable_list)

    @staticmethod
    def _date_range_iterator(list_of_list_of_asset_parameters: list[list[AssetParameters]], variable_list: list) -> pd.DataFrame:

        dataframes = []

        for list_of_asset_parameters in list_of_list_of_asset_parameters:

            csv_name = fu.get_base_of_merged_csv_filename(list_of_asset_parameters)
            csv_path = Path(MERGED_CSVS_NEST_CATALOG) / f"{csv_name}.csv"

            oss = OrderBookSessionSimulator()
            orderbook_metrics_entry_list = oss.compute_variables(str(csv_path), variable_list)

            df = pd.DataFrame(
                [
                    {var: getattr(entry, var) for var in variable_list}
                    for entry in orderbook_metrics_entry_list
                ]
            )

            dataframes.append(df)

        if dataframes:
            return pd.concat(dataframes, ignore_index=True)
        else:
            raise Exception('merged df is empty for: ')
