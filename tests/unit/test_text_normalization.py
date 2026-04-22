from __future__ import annotations

import unittest

from backend.services.shared.text_normalization import repair_mojibake


class TextNormalizationTests(unittest.TestCase):
    def test_repairs_common_utf8_gbk_mojibake(self) -> None:
        self.assertEqual(repair_mojibake("鏁欒偛鑳屾櫙"), "教育背景")
        self.assertEqual(repair_mojibake("宀椾綅"), "岗位")


if __name__ == "__main__":
    unittest.main()
