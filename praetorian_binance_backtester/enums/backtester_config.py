from dataclasses import dataclass, field
from pathlib import Path

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_strategies import Strategy
from praetorian_binance_backtester.enums.market import Market
from praetorian_binance_backtester.enums.stream_type import StreamType
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu


MERGED_CSVS_NEST_CATALOG = str(Path.home() / "Documents" / "merged_csvs")
LEARNING_PROCESS_AMOUNT = 3


@dataclass(slots=True)
class BacktesterConfig:
    learn_date_range: list[str]
    backtest_date_range: list[str]
    pairs: list[str]
    markets: list[str | Market]
    stream_types: list[str | StreamType]
    join_pairs_into_one_csv: bool
    join_markets_into_one_csv: bool
    strategies: list[Strategy]

    common_variables: list[str] = field(init=False)

    learn_list_of_merged_list_of_asset_parameters: list[list[AssetParameters]] = field(init=False)
    backtest_list_of_merged_list_of_asset_parameters: list[list[AssetParameters]] = field(init=False)

    def __post_init__(self):
        self.pairs = [pair.upper() for pair in self.pairs]

        self.markets = [
            m if isinstance(m, Market) else Market(m.lower())
            for m in self.markets
        ]

        self.stream_types = [
            s if isinstance(s, StreamType) else StreamType(s.lower())
            for s in self.stream_types
        ]

        self.learn_list_of_merged_list_of_asset_parameters = fu.get_list_of_merged_list_of_asset_parameters(
            date_range=self.learn_date_range,
            pairs=self.pairs,
            markets=self.markets,
            stream_types=self.stream_types,
            should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
            should_join_markets_into_one_csv=self.join_markets_into_one_csv
        )
        self.backtest_list_of_merged_list_of_asset_parameters = fu.get_list_of_merged_list_of_asset_parameters(
            date_range=self.backtest_date_range,
            pairs=self.pairs,
            markets=self.markets,
            stream_types=self.stream_types,
            should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
            should_join_markets_into_one_csv=self.join_markets_into_one_csv
        )

        self.common_variables = list(
            dict.fromkeys(
                var
                for strat in self.strategies
                for var in strat.strategy_config.variable_list
            )
        )
