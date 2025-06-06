from praetorian_strategies import StrategyPool

from legatus_binance_deputy import DeputyRegistry
from legatus_binance_deputy import DeputyMode

from praetorian_binance_backtester.utils.colors import Colors
from praetorian_binance_backtester.utils.logo import logo2, spqr_art2
from praetorian_binance_backtester.utils.time_utils import measure_time
from praetorian_binance_backtester.core.backtest_session import BacktestSession
from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig


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

    @measure_time
    def run_backtest(self) -> None:
        print(f'{Colors.MAGENTA}{spqr_art2}')
        print(f'{Colors.CYAN}{logo2}')
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

        backtest_order_book_metrics_entry_df = backtest_session.get_backtest_order_book_metrics_entry_df(
            self.backtester_config.cpp_order_book_variables_with_common_features
        )

        self.strategy_pool.show_strategies_summary(backtest_order_book_metrics_entry_df)
