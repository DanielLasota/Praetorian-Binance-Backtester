from praetorian_strategies import StrategyPool
from praetorian_binance_backtester.core.backtest_session import BacktestSession
from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig, MERGED_CSVS_NEST_CATALOG


class Backtester:

    __slots__ = [
        'config',
        'strategy_pool',
    ]

    def __init__(
            self,
            config: BacktesterConfig
    ):
        self.config = config
        self.strategy_pool = StrategyPool(config.strategies)

    def run(self) -> None:

        learn_df = LearnSession.learn(
            list_of_list_of_asset_parameters=self.config.learn_list_of_merged_list_of_asset_parameters,
            variables=self.config.cpp_order_book_variables_with_common_features
        )

        self.strategy_pool.teach_strategies(learn_df)

        BacktestSession.run(
            list_of_list_of_asset_parameters=self.config.backtest_list_of_merged_list_of_asset_parameters,
            variables=self.config.cpp_order_book_variables_with_common_features,
            python_callback=self.strategy_pool.inform_strategies
        )

        learn_df.to_csv(f'{MERGED_CSVS_NEST_CATALOG}/x.csv', index=False)


