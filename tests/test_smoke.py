"""Small reproducible smoke tests for the delivered system."""

from __future__ import annotations

import unittest

from app import predict_sentiment
from src.text_utils import detect_language, normalize_text


class TextUtilityTests(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("منتج ممتاز"), "ar")
        self.assertEqual(detect_language("excellent product"), "en")

    def test_arabic_normalization(self):
        self.assertEqual(normalize_text("إِعــلانٌ رائِع"), "اعلان رائع")


class ModelSmokeTests(unittest.TestCase):
    def assert_binary_prediction(self, text: str, expected: str):
        result = predict_sentiment(text)
        self.assertEqual(result["base_binary_label"], expected)
        self.assertGreaterEqual(result["confidence"], 0.50)

    def test_english_positive(self):
        self.assert_binary_prediction("This product is excellent and I love it", "positive")

    def test_english_negative(self):
        self.assert_binary_prediction("This is terrible and a complete waste of money", "negative")

    def test_arabic_positive(self):
        self.assert_binary_prediction("منتج ممتاز ورائع وأنا سعيد به", "positive")

    def test_arabic_negative(self):
        self.assert_binary_prediction("الخدمة سيئة ومخيبة للآمال", "negative")

    def test_prediction_contract(self):
        result = predict_sentiment("Great service and excellent quality")
        expected_keys = {
            "detected_language",
            "base_binary_label",
            "label",
            "label_en",
            "label_ar",
            "confidence",
            "probabilities",
            "uncertainty_threshold",
        }
        self.assertTrue(expected_keys.issubset(result))
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            predict_sentiment("   ")


if __name__ == "__main__":
    unittest.main()
