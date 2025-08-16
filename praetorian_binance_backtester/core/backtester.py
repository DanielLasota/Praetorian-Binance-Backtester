from praetorian_binance_backtester.core import backtest_session
from praetorian_strategies import StrategyPool

from legatus_binance_deputy import DeputyRegistry
from legatus_binance_deputy import DeputyMode

from praetorian_binance_backtester.utils.colors import Colors
from praetorian_binance_backtester.utils.logo import logo2, spqr_art2
from praetorian_binance_backtester.core.backtest_session import BacktestSession
from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig


class Backtester:

    __slots__ = [
        'backtester_config',
        'strategy_pool',
        'backtest_session',
    ]

    def __init__(
            self,
            config: BacktesterConfig
    ):
        self.backtester_config = config
        self.strategy_pool = StrategyPool(config.strategies)
        self.backtest_session = BacktestSession(callback=self.strategy_pool.inform_strategies)

    def run_backtest(self) -> None:
        print(f'{Colors.MAGENTA}{spqr_art2}')
        print(f'{Colors.CYAN}{logo2}')
        deputy = DeputyRegistry.get_deputy(mode=DeputyMode.BACKTEST, name='daniel')

        self.epoch_loop()

        deputy.force_zero_crypto_account_balance(
            final_order_book_metrics_entry=self.backtest_session.get_final_order_book_metrics_entry()
        )

        backtest_df = self.backtest_session.get_backtest_order_book_metrics_entry_df()

        print(f'deputy.get_account_balance() {deputy.get_account_balance_usdt():.2f}')
        print(f'deputy.get_account_balance_crypto() {deputy.get_account_balance_crypto("TRXUSDT")}')

        self.strategy_pool.show_strategies_summary(backtest_df)

    def epoch_loop(self) -> None:
        for learn_epoch, backtest_epoch in zip(self.backtester_config.learn_list_of_merged_list_of_asset_parameters,
                                               self.backtester_config.backtest_list_of_merged_list_of_asset_parameters):
            # print(f'\nlearn_epoch')
            # for ap_list in learn_epoch:
            #     for ap in ap_list:
            #         print(ap)
            # print(f'\nbacktest_epoch')
            # for ap_list in backtest_epoch:
            #     for ap in ap_list:
            #         print(ap)
            # print(f'>>>>>>')

            learn_df = LearnSession.compute_variables_df(
                list_of_list_of_asset_parameters=learn_epoch,
                variables=self.backtester_config.cpp_order_book_variables_with_common_features
            )

            self.strategy_pool.teach_strategies(learn_df)

            self.backtest_session.run(
                list_of_list_of_asset_parameters=backtest_epoch,
                variables=self.backtester_config.cpp_order_book_variables_with_common_features,
                save_df=True
            )
