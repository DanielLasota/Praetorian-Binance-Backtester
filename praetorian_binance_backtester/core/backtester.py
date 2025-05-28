from praetorian_binance_backtester.core.learn_session import LearnSession
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig


class Backtester:

    def __init__(self):
        ...

    def run(self, config: BacktesterConfig) -> None:

        learn_df = LearnSession.learn(
            list_of_list_of_asset_parameters=config.learn_list_of_merged_list_of_asset_parameters,
            variable_list=config.strategies[0].strategy_config.variable_list
        )

        print(learn_df)
