from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_binance_backtester.enums.market import Market
from praetorian_binance_backtester.enums.stream_type import StreamType
from praetorian_binance_backtester.utils.time_utils import TimeUtils as tu

class FileUtils:

    __slots__ = ()

    @staticmethod
    def prepare_dump_path_catalog(dump_path) -> None:
        print(dump_path)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)
        os.startfile(dump_path)

    @staticmethod
    def list_files_in_specified_directory(directory_path: str) -> list:
        try:
            files = []
            for root, _, filenames in os.walk(directory_path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    files.append(full_path)
            return files

        except Exception as e:
            print(f"Error whilst listing files: {e}")
            return []

    @staticmethod
    def decode_asset_parameters_from_csv_name(csv_name: str) -> AssetParameters:
        _csv_name = csv_name.replace('.csv', '')

        market_mapping = {
            'spot': Market.SPOT,
            'usd_m_futures': Market.USD_M_FUTURES,
            'coin_m_futures': Market.COIN_M_FUTURES,
        }

        stream_type_mapping = {
            'difference_depth': StreamType.DIFFERENCE_DEPTH_STREAM,
            'trade': StreamType.TRADE_STREAM,
            'depth_snapshot': StreamType.DEPTH_SNAPSHOT,
        }

        market = next((value for key, value in market_mapping.items() if key in _csv_name), None)
        if market is None:
            raise ValueError(f"Unknown market in CSV name: {_csv_name}")

        stream_type = next((value for key, value in stream_type_mapping.items() if key in _csv_name), None)
        if stream_type is None:
            raise ValueError(f"Unknown stream type in CSV name: {_csv_name}")

        pair = (
            f"{_csv_name.split('_')[-3]}_{_csv_name.split('_')[-2]}"
            if market is Market.COIN_M_FUTURES
            else _csv_name.split('_')[-2]
        )

        date = _csv_name.split('_')[-1]

        return AssetParameters(
            market=market,
            stream_type=stream_type,
            pairs=[pair],
            date=date
        )

    @staticmethod
    def get_base_of_blob_file_name(asset_parameters: AssetParameters) -> str:

        if len(asset_parameters.pairs) != 1:
            raise Exception(f"asset_parameters.pairs should've been a string")

        formatted_now_timestamp = get_utc_formatted_timestamp_for_file_name()
        return (
            f"binance"
            f"_{asset_parameters.stream_type.name.lower()}"
            f"_{asset_parameters.market.name.lower()}"
            f"_{asset_parameters.pairs[0].lower()}"
            f"_{formatted_now_timestamp}"
        )

    @staticmethod
    def get_base_of_root_csv_filename(asset_parameters: AssetParameters) -> str:
        return (
            f"binance"
            f"_{asset_parameters.stream_type.name.lower()}"
            f"_{asset_parameters.market.name.lower()}"
            f"_{asset_parameters.pairs[0].lower()}"
            f"_{asset_parameters.date}"
        )

    @staticmethod
    def get_base_of_merged_csv_filename(list_of_asset_parameters_for_single_csv: list[AssetParameters]) -> str:
        stream_types = sorted({ap.stream_type.name.lower() for ap in list_of_asset_parameters_for_single_csv})
        markets = sorted({ap.market.name.lower() for ap in list_of_asset_parameters_for_single_csv})
        pairs = sorted({ap.pairs[0].lower() for ap in list_of_asset_parameters_for_single_csv})
        date = list_of_asset_parameters_for_single_csv[0].date
        return (
            f"binance_merged"
            f"_{'_'.join(stream_types)}"
            f"_{'_'.join(markets)}"
            f"_{'_'.join(pairs)}"
            f"_{date}"
        )

    # @staticmethod
    # def save_df_with_data_quality_reports(dataframe: pd.DataFrame,dataframe_quality_reports: DataQualityReport | list[DataQualityReport],dump_catalog: str,filename: str) -> None:
    #     dump_path = Path(dump_catalog) / f"{filename}.csv"
    #     dump_path.parent.mkdir(parents=True, exist_ok=True)
    #
    #     if isinstance(dataframe_quality_reports, DataQualityReport):
    #         dataframe_quality_reports = [dataframe_quality_reports]
    #
    #     with dump_path.open("w", newline="") as f:
    #         for report in dataframe_quality_reports:
    #             f.write(str(report))
    #             f.write("\n")
    #         dataframe.to_csv(f, index=False, lineterminator="\n")

    @staticmethod
    def get_list_of_merged_list_of_asset_parameters(
            date_range: list[str],
            pairs: list[str],
            markets: list[Market],
            stream_types: list[StreamType],
            should_join_pairs_into_one_csv: bool = False,
            should_join_markets_into_one_csv: bool = False
    ) -> list[list[AssetParameters]]:

        dates = tu.generate_dates_string_list_from_range(date_range)

        groups = []

        # Przypadek 1: Nie łączymy par, nie łączymy rynków – grupujemy wg (pair, market, date)
        if not should_join_pairs_into_one_csv and not should_join_markets_into_one_csv:
            for pair in pairs:
                pair = pair.lower()
                for market in markets:
                    for date in dates:
                        group = []
                        for stream in stream_types:
                            asset_param = AssetParameters(
                                market=Market(market),
                                stream_type=StreamType(stream),
                                pairs=[(f'{pair[:-1]}_perp' if market == Market.COIN_M_FUTURES else pair)],
                                date=date
                            )
                            group.append(asset_param)
                        groups.append(group)

        # Przypadek 2: Nie łączymy par, łączymy rynki – grupujemy wg (pair, date) (wszystkie rynki w jednej grupie)
        elif not should_join_pairs_into_one_csv and should_join_markets_into_one_csv:
            for pair in pairs:
                pair = pair.lower()
                for date in dates:
                    group = []
                    for market in markets:
                        for stream in stream_types:
                            asset_param = AssetParameters(
                                market=Market(market),
                                stream_type=StreamType(stream),
                                pairs=[(f'{pair[:-1]}_perp' if market == Market.COIN_M_FUTURES else pair)],
                                date=date
                            )
                            group.append(asset_param)
                    groups.append(group)

        # Przypadek 3: Łączymy pary, nie łączymy rynków – grupujemy wg (market, date) (wszystkie pary w jednej grupie)
        elif should_join_pairs_into_one_csv and not should_join_markets_into_one_csv:
            for market in markets:
                for date in dates:
                    group = []
                    for pair in pairs:
                        pair = pair.lower()
                        for stream in stream_types:
                            asset_param = AssetParameters(
                                market=Market(market),
                                stream_type=StreamType(stream),
                                pairs=[(f'{pair[:-1]}_perp' if market == Market.COIN_M_FUTURES else pair)],
                                date=date
                            )
                            group.append(asset_param)
                    groups.append(group)

        # Przypadek 4: Łączymy pary i łączymy rynki – grupujemy wg daty (wszystkie pary i rynki w jednej grupie)
        else:  # should_join_pairs_into_one_csv and should_join_markets_into_one_csv
            for date in dates:
                group = []
                for pair in pairs:
                    pair = pair.lower()
                    for market in markets:
                        for stream in stream_types:
                            asset_param = AssetParameters(
                                market=Market(market),
                                stream_type=StreamType(stream),
                                pairs=[(f'{pair[:-1]}_perp' if market == Market.COIN_M_FUTURES else pair)],
                                date=date
                            )
                            group.append(asset_param)
                groups.append(group)

        return groups
