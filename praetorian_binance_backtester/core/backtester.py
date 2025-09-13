from praetorian_binance_backtester.enums.asset_parameters import AssetParameters
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
        Backtester.print_entry_screen()
        deputy = DeputyRegistry.get_deputy(mode=DeputyMode.BACKTEST, name='daniel')

        self.main_backtester_loop()

        deputy.force_zero_crypto_account_balance(self.backtest_session.get_final_order_book_metrics_entry())

        backtest_df = self.backtest_session.get_backtest_order_book_metrics_entry_df()

        self.strategy_pool.show_strategies_summary(backtest_df)

    @staticmethod
    def print_entry_screen():
        print(f'{Colors.MAGENTA}{spqr_art2}')
        print(f'{Colors.CYAN}{logo2}')

    def main_backtester_loop(self) -> None:
        for epoch in self.backtester_config.backtester_epochs:
            self.single_epoch_loop(epoch)

    def single_epoch_loop(
            self,
            backtester_epoch: tuple[list[list[AssetParameters]], list[list[AssetParameters]]],
    ) -> None:
        learn_epoch = backtester_epoch[0]
        backtest_epoch = backtester_epoch[1]
        print(f'>>>>>>')
        print(f'learn_epoch')
        for ap_list in learn_epoch:
            for ap in ap_list:
                print(ap)
        print(f'backtest_epoch')
        for ap_list in backtest_epoch:
            for ap in ap_list:
                print(ap)
        print(f'>>>>>>')
        print()

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
