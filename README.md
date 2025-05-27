# Praetorian Binance Backtester
## A Package for conducting backtests on binance historical data
## Package uses cpp_binance_orderbook

```bash
pip install praetorian-binance-backtester
```

### Functions:
1. learn on specified period
2. auto-analysis (OLS variables etc)
3. production strategy in backtest mode (The same strategy as in production, but instead of placing real orders on Binance, it places paper (simulated) orders)
3. conduct backtest based on learn time period
4. print results / pnl 

### Handles:
#### Markets:
spot  
futures usd-m  
futures coin-m

#### Sources:
difference depth stream  
trade stream  
depth snapshot request


