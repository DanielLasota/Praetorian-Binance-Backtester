import time

from praetorian_binance_backtester import Backtester
from praetorian_binance_backtester import OLSStrategy
from praetorian_binance_backtester import OLSStrategyConfig
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig


if __name__ == '__main__':

    ols1_strategy = OLSStrategy(
        strategy_config=OLSStrategyConfig(
            buy_from=100,
            sell_from=-100,
            variable_list=['timestampOfReceive', 'market', 'symbol', 'bestAskPrice', 'bestBidPrice'],
            coefficients=[]
        )
    )

    config = BacktesterConfig(
        learn_date_range=['21-05-2025', '23-05-2025'],
        backtest_date_range=['24-05-2025', '24-05-2025'],
        pairs=[
            "TRXUSDT",
        ],
        markets=[
            # 'SPOT',
            'USD_M_FUTURES',
            # 'COIN_M_FUTURES'
        ],
        stream_types=[
            'TRADE_STREAM',
            'DIFFERENCE_DEPTH_STREAM',
            'DEPTH_SNAPSHOT'
        ],
        join_pairs_into_one_csv=False,
        join_markets_into_one_csv=False,
        strategies=[ols1_strategy]
    )
    backtester = Backtester()

    start_time = time.time()
    backtester.run(config=config)
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time of backtester.run: {execution_time:.2f} seconds")
