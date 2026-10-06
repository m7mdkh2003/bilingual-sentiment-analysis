"""Command-line interface for the bilingual sentiment classifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib

from src.text_utils import detect_language, normalize_text


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "best_model.joblib"
METADATA_PATH = ROOT / "models" / "metadata.json"


def load_artifacts():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Model files are missing. Run: python -m src.prepare_data && python -m src.train"
        )
    return (
        joblib.load(MODEL_PATH),
        json.loads(METADATA_PATH.read_text(encoding="utf-8")),
    )


def predict_sentiment(text: str) -> dict:
    model, metadata = load_artifacts()
    normalized = normalize_text(text)
    if not normalized:
        raise ValueError("Please enter a non-empty review / الرجاء إدخال مراجعة نصية")
    probabilities = model.predict_proba([normalized])[0]
    classes = list(model.classes_)
    best_index = int(probabilities.argmax())
    base_label = classes[best_index]
    confidence = float(probabilities[best_index])
    threshold = float(metadata["neutral_uncertainty_threshold"])
    uncertain = confidence < threshold
    output_label = "uncertain" if uncertain else base_label
    bilingual = {
        "positive": {"en": "Positive", "ar": "إيجابي"},
        "negative": {"en": "Negative", "ar": "سلبي"},
        "uncertain": {"en": "Neutral / uncertain", "ar": "محايد / غير مؤكّد"},
    }[output_label]
    class_probabilities = {
        label: float(probabilities[classes.index(label)]) for label in classes
    }
    return {
        "text": text,
        "detected_language": detect_language(text),
        "normalized_text": normalized,
        "base_binary_label": base_label,
        "label": output_label,
        "label_en": bilingual["en"],
        "label_ar": bilingual["ar"],
        "confidence": confidence,
        "probabilities": class_probabilities,
        "uncertainty_threshold": threshold,
        "note_en": "Neutral is an uncertainty output, not a separately trained class."
        if uncertain
        else "Binary model prediction.",
        "note_ar": "المحايد هنا يعني أن ثقة النموذج منخفضة، وليس فئة مدرّبة مستقلة."
        if uncertain
        else "تنبؤ صادر عن نموذج ثنائي الفئات.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arabic-English sentiment analysis / تحليل المشاعر العربي والإنجليزي"
    )
    parser.add_argument("--text", help="Review text / نص المراجعة")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    text = args.text
    if text is None:
        text = input("Enter a review / أدخل المراجعة: ").strip()
    result = predict_sentiment(text)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"Result / النتيجة: {result['label_en']} - {result['label_ar']}")
    print(f"Confidence / الثقة: {result['confidence']:.1%}")
    print(f"Language / اللغة: {result['detected_language']}")
    print(result["note_en"])
    print(result["note_ar"])


if __name__ == "__main__":
    main()

