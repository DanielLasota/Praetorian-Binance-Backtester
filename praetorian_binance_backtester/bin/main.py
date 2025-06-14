from praetorian_strategies import OLSStrategy
from praetorian_strategies import OLSStrategyConfig

from praetorian_binance_backtester import Backtester
from praetorian_binance_backtester.enums.backtester_config import BacktesterConfig


if __name__ == '__main__':

    ols1_strategy = OLSStrategy(
        strategy_config=OLSStrategyConfig(
            strategy_name='ols1_strategy',
            buy_from=0.0000_30,
            sell_from=-0.0000_30,
            quantity=1000,
            features=[
                'bestVolumeImbalance',
                'queueImbalance',
                'volumeImbalance'
            ],
            coefficients=[],
            mid_price_diff_seconds=20,
            global_tan_h=False,
            single_features_to_be_tan_h=[
                # 'queueImbalance',
                # 'volumeImbalance'
            ],
            add_constant=False,
            starting_funds_usdt=100_000
        )
    )

    config = BacktesterConfig(
        learn_date_range=['19-05-2025', '19-05-2025'],
        backtest_date_range=['20-05-2025', '23-05-2025'],
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
        strategies=[
            ols1_strategy
        ]
    )
    backtester = Backtester(config=config)
    backtester.run_backtest()
