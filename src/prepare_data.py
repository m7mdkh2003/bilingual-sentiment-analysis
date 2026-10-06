"""Build the reproducible bilingual dataset used by the project."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

try:
    from src.text_utils import normalize_text
except ModuleNotFoundError:
    from text_utils import normalize_text


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def stable_id(language: str, source: str, text: str) -> str:
    value = f"{language}|{source}|{text}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:16]


def load_english_reviews() -> list[dict]:
    rows: list[dict] = []
    for source in ("amazon", "imdb", "yelp"):
        data = json.loads((RAW / f"{source}.json").read_text(encoding="utf-8"))
        for item in data:
            text = str(item.get("text") or "").strip()
            raw_class = item.get("class")
            if not text or raw_class not in (0, 1):
                continue
            label = "positive" if raw_class == 1 else "negative"
            normalized = normalize_text(text)
            if not normalized:
                continue
            rows.append(
                {
                    "id": stable_id("en", source, text),
                    "text": text,
                    "text_normalized": normalized,
                    "label": label,
                    "language": "en",
                    "source": f"UCI-{source}",
                    "lexicon_score": "",
                }
            )
    return rows


def load_arabic_lexicon() -> list[dict]:
    lexicon = json.loads((RAW / "AFINN-ar.json").read_text(encoding="utf-8"))
    rows: list[dict] = []
    for term, score in lexicon.items():
        term = str(term).strip()
        score = int(score)
        if not term or score == 0:
            continue
        normalized = normalize_text(term)
        if len(normalized) < 2:
            continue
        label = "positive" if score > 0 else "negative"
        rows.append(
            {
                "id": stable_id("ar", "AFINN-ar", term),
                "text": term,
                "text_normalized": normalized,
                "label": label,
                "language": "ar",
                "source": "AFINN-ar-translated-lexicon",
                "lexicon_score": score,
            }
        )
    return rows


def deduplicate(rows: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    result: list[dict] = []
    for row in rows:
        key = (row["language"], row["text_normalized"])
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    rows = deduplicate(load_english_reviews() + load_arabic_lexicon())
    fieldnames = [
        "id",
        "text",
        "text_normalized",
        "label",
        "language",
        "source",
        "lexicon_score",
    ]
    output_path = PROCESSED / "bilingual_sentiment_dataset.csv"
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    language_counts = Counter(row["language"] for row in rows)
    label_counts = Counter(row["label"] for row in rows)
    source_counts = Counter(row["source"] for row in rows)
    language_label_counts = Counter(
        f"{row['language']}_{row['label']}" for row in rows
    )
    summary = {
        "total_records": len(rows),
        "language_counts": dict(sorted(language_counts.items())),
        "label_counts": dict(sorted(label_counts.items())),
        "language_label_counts": dict(sorted(language_label_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "english_component": "UCI Sentiment Labelled Sentences review sentences",
        "arabic_component": "Translated AFINN Arabic sentiment terms; not full review sentences",
    }
    (PROCESSED / "dataset_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

