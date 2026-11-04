"""Unit tests for the evidence check in demo/CoT_Module.py.

Run:  python -m unittest discover tests
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "demo"))
from CoT_Module import EVIDENCE_MATCH_THRESHOLD, evidence_score, find_homoglyph_words  # noqa: E402

# Exam email E16 (data/test index 276): "Keep My Password" written with Cyrillic
# look-alikes and zero-width no-break spaces (U+FEFF) between the letters.
E16_TEST_INDEX = 276
ZW = chr(0xFEFF)
CYR_IE, CYR_ER, CYR_A = chr(0x0435), chr(0x0420), chr(0x0430)
E16_EXCERPT = (f"K{CYR_IE}{ZW}{ZW}{CYR_IE}{ZW}{ZW}p M{ZW}y "
               f"{CYR_ER}{ZW}{ZW}{CYR_A}{ZW}{ZW}ss{ZW}w{ZW}{ZW}or{ZW}d Thank You")


class EvidenceMatchTest(unittest.TestCase):
    def test_e16_homoglyph_quote_matches_excerpt(self):
        # Model quoted the Latin spelling; before the fix this scored 0.75
        self.assertEqual(evidence_score("Keep My Password", E16_EXCERPT), 1.0)

    def test_e16_homoglyph_quote_matches_real_email(self):
        records = json.loads((ROOT / "data/test/data.json").read_text(encoding="utf-8"))
        email = records[E16_TEST_INDEX]["input"]
        self.assertEqual(evidence_score("Keep My Password", email), 1.0)

    def test_dropped_word_is_not_a_homoglyph_issue(self):
        # The other E16 rejection: subject is "Your email password has expired."
        # and the model dropped "email". That is a paraphrase, not a look-alike
        # character, so it should still fall below the threshold.
        records = json.loads((ROOT / "data/test/data.json").read_text(encoding="utf-8"))
        email = records[E16_TEST_INDEX]["input"]
        self.assertLess(evidence_score("Your password has expired.", email), EVIDENCE_MATCH_THRESHOLD)

    def test_fabricated_quote_still_rejected(self):
        self.assertLess(evidence_score("Your account will be suspended within 24 hours", E16_EXCERPT),
                        EVIDENCE_MATCH_THRESHOLD)


class HomoglyphDetectionTest(unittest.TestCase):
    def test_flags_mixed_script_words(self):
        words = {w["looks_like"] for w in find_homoglyph_words(E16_EXCERPT)}
        self.assertEqual(words, {"Keep", "Password"})

    def test_ignores_plain_latin_and_all_cyrillic_words(self):
        russian = "".join(chr(c) for c in (0x043F, 0x0440, 0x0438, 0x0432, 0x0435, 0x0442))  # "привет"
        self.assertEqual(find_homoglyph_words(f"Keep my password safe. {russian}"), [])


if __name__ == "__main__":
    unittest.main()
