from praetorian_binance_backtester import Backtester
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig
from praetorian_strategies.bin.ols1_strategy import ols1_strategy

if __name__ == '__main__':

    config = BacktesterConfig(
        learn_date_range=['01-08-2025', '04-08-2025'],
        backtest_date_range=['05-08-2025', '06-08-2025'],
        pairs=[
            "BTCUSDT",
            # "XRPUSDT",
            # "SOLUSDT",
        ],
        markets=[
            'SPOT',
            # 'USD_M_FUTURES',
            # 'COIN_M_FUTURES'
        ],
        stream_types=[
            'TRADE_STREAM',
            'DIFFERENCE_DEPTH_STREAM',
            'DEPTH_SNAPSHOT'
        ],
        join_pairs_into_one_csv=False,
        join_markets_into_one_csv=False,
        strategies=[
            ols1_strategy
        ]
    )
    backtester = Backtester(config=config)
    backtester.run_backtest()
