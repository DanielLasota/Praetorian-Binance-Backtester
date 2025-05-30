from praetorian_strategies import StrategyPool
from praetorian_binance_backtester.core.backtest_session import BacktestSession
from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig, MERGED_CSVS_NEST_CATALOG


class Backtester:

    def __init__(
            self,
            config: BacktesterConfig
    ):
        self.config = config
        self.strategy_pool = StrategyPool(config.strategies)

    def run(self) -> None:

        learned_df = LearnSession.learn(
            self.config.learn_list_of_merged_list_of_asset_parameters,
            self.config.common_variables
        )

        self.strategy_pool.teach_strategies(learned_df)

        BacktestSession.run(
            self.config.backtest_list_of_merged_list_of_asset_parameters,
            self.config.common_variables,
            self.strategy_pool.inform_strategies
        )

        # learned_df.to_csv(f'{MERGED_CSVS_NEST_CATALOG}/x.csv', index=False)
