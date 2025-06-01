from legatus_binance_deputy.core.deputy_registry import DeputyRegistry
from legatus_binance_deputy.enums.deputy_mode import DeputyMode
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
        deputy = DeputyRegistry.get_deputy(mode=DeputyMode.BACKTEST, name='daniel')

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

        print(f'deputy.get_account_balance() {deputy.get_account_balance_usdt():.2f}')
        print(f'deputy.get_account_balance_crypto() {deputy.get_account_balance_crypto("TRXUSDT")}')
        for _ in deputy.get_deputy_order_list():
            print(_)

        # learn_df.to_csv(f'{MERGED_CSVS_NEST_CATALOG}/x.csv', index=False)
