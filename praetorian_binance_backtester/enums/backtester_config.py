from dataclasses import dataclass, field
from datetime import datetime, timedelta

from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
from praetorian_strategies import Strategy, OLSStrategy
from praetorian_binance_backtester.enums.market import Market
from praetorian_binance_backtester.enums.stream_type import StreamType
from praetorian_binance_backtester.utils.file_utils import FileUtils as fu


MERGED_CSVS_NEST_CATALOG = 'D:/merged_csvs/'
LEARNING_PROCESS_AMOUNT = 4
BASE_CPP_ORDER_BOOK_VARIABLES = [
    'timestampOfReceive',
    'market',
    'symbol',
    'bestAskPrice',
    'bestBidPrice',
    'midPrice'
]

DATE_FMT = "%d-%m-%Y"

def _parse_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, DATE_FMT)
    except Exception as e:
        raise ValueError(f"Bad date format '{s}'. Expected {DATE_FMT}.") from e

def _fmt_date(d: datetime) -> str:
    return d.strftime(DATE_FMT)

def _list_days(start: datetime, days: int) -> list[str]:
    return [_fmt_date(start + timedelta(days=i)) for i in range(days)]


@dataclass(slots=True)
class BacktesterConfig:
    learn_date_range: list[str] | None = None
    backtest_date_range: list[str] | None = None

    start_date: str | None = None
    end_date: str | None = None
    learn_days_amount: int | None = 1
    backtest_day_amount: int | None = 1

    pairs: list[str] = field(default_factory=list)
    markets: list[str | Market] = field(default_factory=list)
    stream_types: list[str | StreamType] = field(default_factory=list)
    join_pairs_into_one_csv: bool = False
    join_markets_into_one_csv: bool = False
    strategies: list[Strategy | OLSStrategy] = field(default_factory=list)

    common_strategies_features: list[str] = field(init=False)
    cpp_order_book_variables_with_common_features: list[str] = field(init=False)

    learn_list_of_merged_list_of_asset_parameters: list[list[list[AssetParameters]]] = field(init=False)
    backtest_list_of_merged_list_of_asset_parameters: list[list[list[AssetParameters]]] = field(init=False)

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

        if None not in (self.learn_date_range, self.backtest_date_range):
            (
                self.learn_list_of_merged_list_of_asset_parameters,
                self.backtest_list_of_merged_list_of_asset_parameters
            ) = self._build_asset_param_lists()
        elif None not in (self.start_date, self.end_date):
            epochs = self._build_rolling_epochs()

            self.learn_list_of_merged_list_of_asset_parameters = []
            self.backtest_list_of_merged_list_of_asset_parameters = []

            for learn_range, backtest_range in epochs:
                learn_params = fu.get_list_of_merged_list_of_asset_parameters(
                    date_range=learn_range,
                    pairs=self.pairs,
                    markets=self.markets,
                    stream_types=self.stream_types,
                    should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
                    should_join_markets_into_one_csv=self.join_markets_into_one_csv
                )
                backtest_params = fu.get_list_of_merged_list_of_asset_parameters(
                    date_range=backtest_range,
                    pairs=self.pairs,
                    markets=self.markets,
                    stream_types=self.stream_types,
                    should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
                    should_join_markets_into_one_csv=self.join_markets_into_one_csv
                )

                self.learn_list_of_merged_list_of_asset_parameters.append(learn_params)
                self.backtest_list_of_merged_list_of_asset_parameters.append(backtest_params)

        self.common_strategies_features = list(
            dict.fromkeys(
                var
                for strat in self.strategies
                for var in strat.strategy_config.features
            )
        )

        self.cpp_order_book_variables_with_common_features = BASE_CPP_ORDER_BOOK_VARIABLES + self.common_strategies_features

    def _build_asset_param_lists(self) -> tuple[list[list[list[AssetParameters]]], list[list[list[AssetParameters]]]]:
        learn = fu.get_list_of_merged_list_of_asset_parameters(
            date_range=self.learn_date_range,
            pairs=self.pairs,
            markets=self.markets,
            stream_types=self.stream_types,
            should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
            should_join_markets_into_one_csv=self.join_markets_into_one_csv
        )

        backtest = fu.get_list_of_merged_list_of_asset_parameters(
            date_range=self.backtest_date_range,
            pairs=self.pairs,
            markets=self.markets,
            stream_types=self.stream_types,
            should_join_pairs_into_one_csv=self.join_pairs_into_one_csv,
            should_join_markets_into_one_csv=self.join_markets_into_one_csv
        )

        for strategy in self.strategies:
            strategy.strategy_config.learn_date_range = self.learn_date_range
            strategy.strategy_config.backtest_date_range = self.backtest_date_range

        return [learn], [backtest]

    def _build_rolling_epochs(self) -> list[tuple[list[str], list[str]]]:
        if not (self.start_date and self.end_date and self.learn_days_amount and self.backtest_day_amount):
            raise ValueError("Tryb rolowany wymaga: start_date, end_date, learn_days_amount, backtest_day_amount.")

        L = int(self.learn_days_amount)
        B = int(self.backtest_day_amount)
        if L <= 0 or B <= 0:
            raise ValueError("learn_days_amount i backtest_day_amount muszą być > 0.")

        start = _parse_date(self.start_date)
        end_inclusive = _parse_date(self.end_date)
        end_exclusive = end_inclusive + timedelta(days=1)

        stride = B
        epochs: list[tuple[list[str], list[str]]] = []

        cursor = start
        while True:
            learn_start = cursor
            learn_end_exclusive = learn_start + timedelta(days=L)
            backtest_start = learn_end_exclusive
            backtest_end_exclusive = backtest_start + timedelta(days=B)

            if backtest_start >= end_exclusive:
                break

            learn_days = min(L, max(0, (end_exclusive - learn_start).days))
            backtest_days = min(B, max(0, (end_exclusive - backtest_start).days))

            if learn_days <= 0 or backtest_days <= 0:
                break

            learn_range = [
                _fmt_date(learn_start),
                _fmt_date(learn_start + timedelta(days=learn_days - 1))
            ]
            backtest_range = [
                _fmt_date(backtest_start),
                _fmt_date(backtest_start + timedelta(days=backtest_days - 1))
            ]

            epochs.append((learn_range, backtest_range))

            cursor = cursor + timedelta(days=stride)
            if cursor >= end_exclusive:
                break

        if not epochs:
            raise ValueError("Nie udało się zbudować żadnej epoki w zadanym zakresie dat.")
        return epochs
