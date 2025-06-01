import time

from legatus_binance_deputy.core.deputy_registry import DeputyRegistry
from legatus_binance_deputy.enums.deputy_mode import DeputyMode
from praetorian_strategies import StrategyPool
from praetorian_binance_backtester.core.backtest_session import BacktestSession
from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig, MERGED_CSVS_NEST_CATALOG


class Backtester:

    __slots__ = [
        'backtester_config',
        'strategy_pool',
    ]

    def __init__(
            self,
            config: BacktesterConfig
    ):
        self.backtester_config = config
        self.strategy_pool = StrategyPool(config.strategies)

    def run(self) -> None:
        deputy = DeputyRegistry.get_deputy(mode=DeputyMode.BACKTEST, name='daniel')

        learn_df = LearnSession.compute_variables_df(
            list_of_list_of_asset_parameters=self.backtester_config.learn_list_of_merged_list_of_asset_parameters,
            variables=self.backtester_config.cpp_order_book_variables_with_common_features
        )

        self.strategy_pool.teach_strategies(learn_df)

        backtest_session = BacktestSession(callback=self.strategy_pool.inform_strategies)
        backtest_session.run(
            list_of_list_of_asset_parameters=self.backtester_config.backtest_list_of_merged_list_of_asset_parameters,
            variables=self.backtester_config.cpp_order_book_variables_with_common_features
        )

        deputy.force_zero_crypto_account_balance(
            final_order_book_metrics_entry=backtest_session.get_final_order_book_metrics_entry()
        )

        backtest_df = backtest_session.get_backtest_entry_df(self.backtester_config.cpp_order_book_variables_with_common_features)
        # print(backtest_df.columns)
        # print(backtest_df)

        print(f'deputy.get_account_balance() {deputy.get_account_balance_usdt():.2f}')
        print(f'deputy.get_account_balance_crypto() {deputy.get_account_balance_crypto("TRXUSDT")}')
        for _ in deputy.get_deputy_order_list():
            print(_)

        for strategy in self.backtester_config.strategies:
            print(strategy.ols_strategy_config.strategy_name)
