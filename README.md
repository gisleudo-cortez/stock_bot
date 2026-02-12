# Stock Bot (Active Tracker)

A Python-based financial monitoring CLI designed to track assets (specifically NASDAQ & Gold), calculate technical indicators, and log strategy decisions.

## 🚀 Features
* **Real-time Tracking**: Monitor `NQ=F` (Nasdaq), `GC=F` (Gold), and others.
* **Technical Stack**: 
  * **uv**: Fast Python package and project management.
  * **Polars**: High-performance data processing.
  * **yfinance**: Market data ingestion.
* **Indicators**:
  * Williams %R (50 period)
  * EMA Spread (4, 8, 20)
  * MACD (4, 12, 3)
  * Linear Regression Trend Angle

## 🛠 Installation

This project uses [uv](https://github.com/astral-sh/uv).

1. **Sync Dependencies**:
   ```bash
   uv sync
