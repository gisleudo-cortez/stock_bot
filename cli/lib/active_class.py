import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import polars as pl
import yfinance as yf
from dotenv import load_dotenv

# Assumes file is at stock_bot/cli/lib/active_class.py
# parents[0] = lib, parents[1] = cli, parents[2] = stock_bot (Root)
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

# Data stored in project root "data/"
DATA_DIR = ROOT_DIR / "data"
HISTORY_DIR = DATA_DIR / "history"
LOGS_DIR = DATA_DIR / "logs"

for d in [HISTORY_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Active_Class")

try:
    from .indicators import ema, macd, williams_r, slope_angle
except ImportError:
    # Fallback if running script directly not as package
    from indicators import ema, macd, williams_r, slope_angle


@dataclass
class Active:
    ticker: str
    interval: str = "15m"  # Configurable interval
    price: float = 0.0
    trend_angle: float = 0.0
    indicators: Dict[str, float] = field(default_factory=dict)
    is_active: bool = False
    _price_buffer: pl.DataFrame = field(
        default_factory=lambda: pl.DataFrame(), repr=False
    )
    _created_at: datetime = field(default_factory=datetime.now, repr=False)
    _decision_log: List[Dict[str, Any]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.log_decision(
            "INITIALIZE", {"ticker": self.ticker, "timestamp": str(self._created_at)}
        )
        self.is_active = True
        logger.info(f"Active initialized: {self.ticker} [{self.interval}]")
        self.refresh_data()

    def refresh_data(self) -> None:
        """Fetches data, calculates indicators (EMA, MACD, WillR), and updates state."""
        try:
            # Fetch adequate history to calculate EMA20 and Williams50
            # 5d is usually safe for intraday 15m/1h intervals
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period="5d", interval=self.interval)

            if hist.empty:
                logger.warning(f"No data for {self.ticker}")
                return

            # Convert to Polars
            df = pl.from_pandas(hist.reset_index())

            # Rename columns to lowercase for consistency
            df = df.rename({c: c.lower() for c in df.columns})

            # --- CALCULATE INDICATORS ---
            # Using logic from indicators.py
            df = df.with_columns(
                [
                    ema("close", 4).alias("ema_4"),
                    ema("close", 8).alias("ema_8"),
                    ema("close", 20).alias("ema_20"),
                    williams_r(df, period=50).alias("williams_r"),
                    slope_angle("close", window=5).alias("trend_angle"),
                ]
            )

            # MACD returns two series, we handle them efficiently
            macd_line, macd_signal = macd(df, fast=4, slow=12, signal=3)
            df = df.with_columns([macd_line, macd_signal])

            # Update State with latest candle
            last_row = df.tail(1).to_dicts()[0]

            self.price = last_row["close"]
            self.trend_angle = (
                last_row["trend_angle"] if last_row["trend_angle"] else 0.0
            )

            self.indicators = {
                "ema_4": last_row["ema_4"],
                "ema_8": last_row["ema_8"],
                "ema_20": last_row["ema_20"],
                "williams_r": last_row["williams_r"],
                "macd_line": last_row["macd_line"],
                "macd_signal": last_row["macd_signal"],
            }

            self._price_buffer = df

            logger.info(
                f"{self.ticker}: {self.price:.2f} | Angle: {self.trend_angle:.1f} | "
                f"WillR: {self.indicators['williams_r']:.1f}"
            )

            self.save_state()
            self._check_strategy_signals()

        except Exception as e:
            logger.error(f"Refresh failed for {self.ticker}: {e}")
            self.log_decision("FETCH_ERROR", {"error": str(e)})

    def _check_strategy_signals(self):
        """Placeholder for Strategy Logic from notes.txt"""
        # Example: EMA Crossover
        if (self.indicators["ema_4"] > self.indicators["ema_8"]) and (
            self.indicators["ema_8"] > self.indicators["ema_20"]
        ):
            # Signal logic here
            pass

    def save_state(self) -> None:
        """Saves the full Polars DataFrame to CSV (Overwriting or Appending logic)."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        csv_file = HISTORY_DIR / f"{self.ticker}_{today_str}.csv"

        # For simplicity/robustness, we write the daily buffer.
        self._price_buffer.write_csv(csv_file)

        # Flush decision logs
        if self._decision_log:
            log_file = LOGS_DIR / f"active_{today_str}.log"
            with open(log_file, "a") as f:
                while self._decision_log:
                    entry = self._decision_log.pop(0)
                    f.write(
                        f"[{entry['timestamp']}] {self.ticker} {entry['action']}: {entry['metadata']}\n"
                    )

    def log_decision(self, action: str, metadata: Dict[str, Any]) -> None:
        self._decision_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "metadata": metadata,
            }
        )

    def __str__(self) -> str:
        return (
            f"TICKER: {self.ticker} ({self.interval})\n"
            f"PRICE:  {self.price}\n"
            f"ANGLE:  {self.trend_angle:.2f}°\n"
            f"VARS:   {self.indicators}\n"
        )
