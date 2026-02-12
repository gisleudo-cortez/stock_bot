import unittest
from unittest.mock import patch, MagicMock
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Adjust path to import from root directory
sys.path.append(str(Path(__file__).resolve().parent.parent / "cli"))
from lib.active_class import Active

# We import the logic from active_cli, ensuring we don't trigger the main loop
from active_cli import parse_interval


class TestActiveSystem(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.history_dir = Path(self.test_dir) / "history"
        self.logs_dir = Path(self.test_dir) / "logs"
        self.history_dir.mkdir()
        self.logs_dir.mkdir()

    def tearDown(self):
        # Clean up temporary directory after tests
        shutil.rmtree(self.test_dir)

    # --- TEST 1: Normalization Logic ---
    def test_angle_normalization(self):
        """
        Verifies that a 10% increase results in the same angle
        regardless of the asset price ($10 vs $1000).
        """
        # We mock yfinance so we don't actually fetch data
        with patch("lib.active_class.yf.Ticker"):
            active = Active("TEST")

            # CASE A: Low Price Asset ($10 -> $11)
            # Inject fake buffer data
            active._price_buffer = [
                {"current_price": 10.0, "market_time": "t1"},
                {"current_price": 10.5, "market_time": "t2"},  # +5%
                {"current_price": 11.0, "market_time": "t3"},  # +10% total
            ]
            angle_low = active._calculate_normalized_angle(window=3)

            # CASE B: High Price Asset ($1000 -> $1100)
            active._price_buffer = [
                {"current_price": 1000.0, "market_time": "t1"},
                {"current_price": 1050.0, "market_time": "t2"},  # +5%
                {"current_price": 1100.0, "market_time": "t3"},  # +10% total
            ]
            angle_high = active._calculate_normalized_angle(window=3)

            # The angles should be identical despite price difference
            self.assertAlmostEqual(angle_low, angle_high, places=2)

            # Verify positive slope (uptrend)
            self.assertTrue(angle_low > 0)
            print(
                f"\n[Test] Normalization Success: Low Price Angle {angle_low:.2f}° == High Price Angle {angle_high:.2f}°"
            )

    # --- TEST 2: Data Persistence ---
    @patch("lib.active_class.HISTORY_DIR")
    @patch("lib.active_class.LOGS_DIR")
    def test_save_state(self, mock_logs_dir, mock_history_dir):
        """
        Verifies that data is correctly written to CSV and Log files.
        """
        # Point the Active class to our temporary test directories
        mock_history_dir.__truediv__.side_effect = lambda x: self.history_dir / x
        mock_logs_dir.__truediv__.side_effect = lambda x: self.logs_dir / x

        with patch("lib.active_class.yf.Ticker"):
            active = Active("AAPL")

            # Simulate a data fetch
            active._price_buffer.append(
                {
                    "ticker": "AAPL",
                    "current_price": 150.0,
                    "market_time": datetime.now(),
                    "updated_at": datetime.now(),
                    "trend_angle": 45.0,
                }
            )
            active.log_decision("TEST_ACTION", {"reason": "unit_test"})

            # Trigger save
            active.save_state()

            # Check CSV existence and content
            csv_files = list(self.history_dir.glob("*.csv"))
            self.assertEqual(len(csv_files), 1)
            with open(csv_files[0], "r") as f:
                content = f.read()
                self.assertIn("150.0", content)
                self.assertIn("AAPL", content)

            # Check Log existence and content
            log_files = list(self.logs_dir.glob("*.log"))
            self.assertEqual(len(log_files), 1)
            with open(log_files[0], "r") as f:
                content = f.read()
                self.assertIn("TEST_ACTION", content)

    # --- TEST 3: CLI Interval Parsing ---
    def test_interval_parsing(self):
        """
        Verifies that time strings are converted to seconds correctly.
        """
        self.assertEqual(parse_interval("30s"), 30)
        self.assertEqual(parse_interval("5m"), 300)
        self.assertEqual(parse_interval("1h"), 3600)
        self.assertEqual(parse_interval("120"), 120)  # Default case


if __name__ == "__main__":
    unittest.main()
