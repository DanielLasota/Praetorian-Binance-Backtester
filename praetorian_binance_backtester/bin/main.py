from praetorian_binance_backtester import Backtester
from praetorian_binance_backtester import OLSStrategy
from praetorian_binance_backtester import OLSStrategyConfig


if __name__ == '__main__':

    ols1_strategy = OLSStrategy(
        strategy_config=OLSStrategyConfig(
            buy_from=100,
            sell_from=-100,
            variables=[],
            coefficients=[]
        )
    )

    backtester = Backtester()
    backtester.run(
        learn_date_range=['20-05-2025', '21-05-2025'],
        backtest_date_range=['22-05-2025', '22-05-2025'],
        strategies=[ols1_strategy]
    )
