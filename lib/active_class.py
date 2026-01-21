import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import polars as pl
import yfinance as yf
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("StockEngine")


@dataclass
class Active:
    ticker: str
    price: float = 0.0
    trend_angle: float = 0.0
    is_active: bool = False
    _price_buffer: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    _created_at: datetime = field(default_factory=datetime.now, repr=False)
    _decision_log: List[Dict[str, Any]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.log_decision(
            "INITIALIZE", {"ticker": self.ticker, "timestamp": str(self._created_at)}
        )
        self.is_active = True
        logger.info(f"Active created and activated: {self.ticker}")
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            stock = yf.Ticker(self.ticker)
            data = stock.history(period="1d", interval="1m")

            if not data.empty:
                new_price = float(data["Close"].iloc[-1])
                market_time = data.index[-1]

                self.trend_angle = self._calculate_new_angle(new_price, window=5)
                self.price = new_price

                self._price_buffer.append(
                    {
                        "ticker": self.ticker,
                        "current_price": self.price,
                        "market_time": market_time,
                        "updated_at": datetime.now(),
                        "trend_angle": self.trend_angle,
                    }
                )

                logger.info(
                    f"Buffered {self.ticker} @ {self.price} [Angle: {self.trend_angle:.2f}°]"
                )
            else:
                logger.warning(f"No data for {self.ticker}")

        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            self.log_decision("FETCH_ERROR", {"error": str(e)})

    def _calculate_new_angle(self, current_price: float, window: int) -> float:
        if len(self._price_buffer) < (window - 1):
            return 0.0

        recent_records = self._price_buffer[-(window - 1) :]
        prices = [r["current_price"] for r in recent_records] + [current_price]

        xs = list(range(len(prices)))
        n = len(xs)

        sum_x = sum(xs)
        sum_y = sum(prices)
        sum_xy = sum(x * y for x, y in zip(xs, prices))
        sum_xx = sum(x * x for x in xs)

        denominator = (n * sum_xx) - (sum_x * sum_x)

        if denominator == 0:
            return 0.0

        slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
        return math.degrees(math.atan(slope))

    def to_polars(self) -> pl.DataFrame:
        if not self._price_buffer:
            return pl.DataFrame(
                schema={
                    "ticker": pl.Utf8,
                    "current_price": pl.Float64,
                    "market_time": pl.Datetime,
                    "updated_at": pl.Datetime,
                    "trend_angle": pl.Float64,
                }
            )
        return pl.DataFrame(self._price_buffer)

    def log_decision(self, action: str, metadata: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "metadata": metadata,
        }
        self._decision_log.append(entry)

    def notify(self, message: str) -> None:
        logger.info(f"[{self.ticker} ALERT]: {message}")

    def update_price(self, new_price: float) -> None:
        self.price = new_price
        logger.debug(f"{self.ticker} price updated to {self.price}")

    def __str__(self) -> str:
        return (
            f"TICKER: {self.ticker}\n"
            f"PRICE: {self.price}\n"
            f"ANGLE: {self.trend_angle:.2f}°\n"
            f"CREATED_AT: {self._created_at}\n"
            f"IS_ACTIVE: {self.is_active}"
        )
