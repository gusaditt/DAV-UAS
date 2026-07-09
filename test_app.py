import unittest
import pandas as pd
import numpy as np
from app import format_rupiah, format_number, calc_delta, weighted_ticket

class TestDashboardHelpers(unittest.TestCase):
    
    def test_format_rupiah(self):
        self.assertEqual(format_rupiah(1200000000000), "Rp 1.2 T")
        self.assertEqual(format_rupiah(1500000000), "Rp 1.5 B")
        self.assertEqual(format_rupiah(3500000), "Rp 3.5 M")
        self.assertEqual(format_rupiah(1500), "Rp 1.5 K")
        self.assertEqual(format_rupiah(500), "Rp 500")
        self.assertEqual(format_rupiah(-1500), "-Rp 1.5 K")
        self.assertEqual(format_rupiah(0), "Rp 0")

    def test_format_number(self):
        self.assertEqual(format_number(1200000000), "1.2 B")
        self.assertEqual(format_number(1500000), "1.50 M")
        self.assertEqual(format_number(3500), "3.5 K")
        self.assertEqual(format_number(500), "500")
        self.assertEqual(format_number(-3500), "-3.5 K")
        self.assertEqual(format_number(0), "0")

    def test_calc_delta(self):
        self.assertAlmostEqual(calc_delta(120, 100), 20.0)
        self.assertAlmostEqual(calc_delta(80, 100), -20.0)
        self.assertEqual(calc_delta(100, 0), None)
        self.assertEqual(calc_delta(100, None), None)

    def test_weighted_ticket(self):
        # Empty dataframe case
        df_empty = pd.DataFrame(columns=["total_transactions", "total_revenue"])
        self.assertEqual(weighted_ticket(df_empty), 0.0)
        
        # Non-empty dataframe case
        df_data = pd.DataFrame({
            "total_transactions": [10, 20],
            "total_revenue": [100000, 300000]
        })
        self.assertEqual(weighted_ticket(df_data), 400000 / 30)

if __name__ == "__main__":
    unittest.main()
