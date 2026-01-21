import polars as pl


def williams_r(df: pl.DataFrame, period: int = 50) -> pl.Expr:
    high = pl.col("high").rolling_max(window_size=period)
    low = pl.col("low").rolling_min(window_size=period)
    close = pl.col("close")
    return -100 * ((high - close) / (high - low))


def ema(column: str, period: int) -> pl.Expr:
    return pl.col(column).ewm_mean(span=period, adjust=False)


def slope_angle(column: str, window: int = 5) -> pl.Expr:
    return (pl.col(column) - pl.col(column).shift(window)) / window


def macd(df: pl.DataFrame, fast: int = 4, slow: int = 12, signal: int = 3):
    ema_fast = pl.col("close").ewm_mean(span=fast, adjust=False)
    ema_slow = pl.col("close").ewm_mean(span=slow, adjust=False)
    macd_line = ema_fast - ema_slow
    signal_line = macd.ewm_mean(span=signal, adjust=False)
    return macd_line.alias("macd_line"), signal_line.alias("macd_signal")
