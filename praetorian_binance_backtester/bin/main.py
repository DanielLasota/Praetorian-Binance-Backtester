from praetorian_binance_backtester import Backtester
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig
from praetorian_strategies.bin.cherubim_ols_strategy1 import cherubim_ols_strategy1

if __name__ == '__main__':

    config = BacktesterConfig(
        # learn_date_range=['02-08-2025', '06-08-2025'],
        # backtest_date_range=['07-08-2025', '07-08-2025'],
        start_date='16-09-2025',
        end_date='17-09-2025',
        learn_days_amount=1,
        backtest_day_amount=1,
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
            cherubim_ols_strategy1
        ]
    )
    backtester = Backtester(config=config)
    backtester.run_backtest()
