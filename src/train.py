"""Train, compare, evaluate, and persist bilingual sentiment classifiers."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
(ROOT / ".mplconfig").mkdir(parents=True, exist_ok=True)

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


DATA_PATH = ROOT / "data" / "processed" / "bilingual_sentiment_dataset.csv"
SUMMARY_PATH = ROOT / "data" / "processed" / "dataset_summary.json"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
LABELS = ["negative", "positive"]
RANDOM_STATE = 42
NEUTRAL_THRESHOLD = 0.60


def vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=60000,
        sublinear_tf=True,
        norm="l2",
    )


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def scalar_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(
            y_true, y_pred, labels=LABELS, average="macro", zero_division=0
        ),
        "recall_macro": recall_score(
            y_true, y_pred, labels=LABELS, average="macro", zero_division=0
        ),
        "f1_macro": f1_score(
            y_true, y_pred, labels=LABELS, average="macro", zero_division=0
        ),
    }


def subgroup_metrics(test_df: pd.DataFrame, predictions: np.ndarray, column: str) -> dict:
    output = {}
    for value in sorted(test_df[column].unique()):
        mask = test_df[column].eq(value).to_numpy()
        output[str(value)] = {
            "records": int(mask.sum()),
            **scalar_metrics(test_df.loc[mask, "label"], predictions[mask]),
        }
    return output


def make_model_comparison_chart(model_results: dict) -> None:
    names = list(model_results)
    accuracy = [model_results[n]["test"]["accuracy"] * 100 for n in names]
    f1 = [model_results[n]["test"]["f1_macro"] * 100 for n in names]
    x = np.arange(len(names))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars1 = ax.bar(x - width / 2, accuracy, width, label="Accuracy", color="#0B7285")
    bars2 = ax.bar(x + width / 2, f1, width, label="Macro F1", color="#F59F00")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score (%)")
    ax.set_title("Bilingual hold-out performance")
    ax.set_xticks(x, names)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    ax.bar_label(bars1, fmt="%.1f", padding=3, fontsize=8)
    ax.bar_label(bars2, fmt="%.1f", padding=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "model_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_language_chart(model_results: dict) -> None:
    names = list(model_results)
    languages = ["en", "ar"]
    x = np.arange(len(names))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for idx, language in enumerate(languages):
        values = [
            model_results[n]["by_language"][language]["f1_macro"] * 100
            for n in names
        ]
        offset = (-width / 2) if idx == 0 else (width / 2)
        bars = ax.bar(
            x + offset,
            values,
            width,
            label="English reviews" if language == "en" else "Arabic lexicon",
            color="#1971C2" if language == "en" else "#2F9E44",
        )
        ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Macro F1 (%)")
    ax.set_title("Performance by language component")
    ax.set_xticks(x, names)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "language_f1.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_confusion_chart(y_true, y_pred, model_name: str) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=LABELS)
    fig, ax = plt.subplots(figsize=(4.8, 4.1))
    display = ConfusionMatrixDisplay(matrix, display_labels=["Negative", "Positive"])
    display.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title(f"Confusion matrix: {model_name}")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_architecture_chart() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.2))
    ax.axis("off")
    steps = [
        ("Arabic / English\nreview", "#E7F5FF"),
        ("Unicode and Arabic\nnormalization", "#D0EBFF"),
        ("Character n-gram\nTF-IDF", "#A5D8FF"),
        ("Selected ML\nclassifier", "#74C0FC"),
        ("Positive / Negative\nor uncertain", "#4DABF7"),
    ]
    xs = np.linspace(0.09, 0.91, len(steps))
    for i, ((label, color), x) in enumerate(zip(steps, xs)):
        ax.text(
            x,
            0.52,
            label,
            ha="center",
            va="center",
            fontsize=10,
            bbox={"boxstyle": "round,pad=0.6", "fc": color, "ec": "#1864AB"},
        )
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(xs[i + 1] - 0.09, 0.52),
                xytext=(x + 0.09, 0.52),
                arrowprops={"arrowstyle": "->", "lw": 1.7, "color": "#1864AB"},
            )
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "system_architecture.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        raise SystemExit("Dataset not found. Run: python -m src.prepare_data")

    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig").dropna(
        subset=["text_normalized", "label", "language", "source"]
    )
    df["stratum"] = df["language"] + "_" + df["label"]
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=df["stratum"],
    )
    X_train = train_df["text_normalized"]
    y_train = train_df["label"]
    X_test = test_df["text_normalized"]
    y_test = test_df["label"]

    model_specs = {
        "Logistic Regression": LogisticRegression(
            C=3.0,
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear",
            random_state=RANDOM_STATE,
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.35),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    model_results = {}
    fitted_models = {}
    predictions_by_model = {}

    for name, classifier in model_specs.items():
        pipeline = Pipeline([("tfidf", vectorizer()), ("classifier", classifier)])
        cv_scores = cross_validate(
            pipeline,
            df["text_normalized"],
            df["label"],
            cv=cv,
            scoring={"accuracy": "accuracy", "f1_macro": "f1_macro"},
            n_jobs=1,
        )
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        model_results[name] = {
            "test": scalar_metrics(y_test, predictions),
            "cross_validation": {
                "folds": 5,
                "accuracy_mean": float(cv_scores["test_accuracy"].mean()),
                "accuracy_std": float(cv_scores["test_accuracy"].std()),
                "f1_macro_mean": float(cv_scores["test_f1_macro"].mean()),
                "f1_macro_std": float(cv_scores["test_f1_macro"].std()),
            },
            "by_language": subgroup_metrics(test_df, predictions, "language"),
            "by_source": subgroup_metrics(test_df, predictions, "source"),
            "classification_report": classification_report(
                y_test,
                predictions,
                labels=LABELS,
                output_dict=True,
                zero_division=0,
            ),
            "confusion_matrix": confusion_matrix(
                y_test, predictions, labels=LABELS
            ).tolist(),
        }
        fitted_models[name] = pipeline
        predictions_by_model[name] = predictions

    selected_name = max(
        model_results,
        key=lambda name: model_results[name]["test"]["f1_macro"],
    )
    selected_model = fitted_models[selected_name]
    selected_predictions = predictions_by_model[selected_name]
    feature_count = len(selected_model.named_steps["tfidf"].vocabulary_)
    joblib.dump(selected_model, MODELS_DIR / "best_model.joblib")

    probabilities = selected_model.predict_proba(X_test)
    confidence = probabilities.max(axis=1)
    prediction_output = test_df[
        ["id", "text", "label", "language", "source"]
    ].copy()
    prediction_output["predicted_label"] = selected_predictions
    prediction_output["confidence"] = confidence
    prediction_output["correct"] = prediction_output["label"].eq(
        prediction_output["predicted_label"]
    )
    prediction_output.to_csv(
        RESULTS_DIR / "test_predictions.csv", index=False, encoding="utf-8-sig"
    )

    dataset_summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    report_data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "neutral_uncertainty_threshold": NEUTRAL_THRESHOLD,
        "dataset": dataset_summary,
        "split": {"train_records": len(train_df), "test_records": len(test_df)},
        "feature_extraction": {
            "type": "character n-gram TF-IDF",
            "ngram_range": [3, 5],
            "feature_count_selected_model": feature_count,
        },
        "selected_model": selected_name,
        "models": model_results,
        "important_limitations": [
            "English evaluation uses held-out review sentences from UCI.",
            "Arabic evaluation uses held-out translated AFINN sentiment terms, not a full Arabic review corpus.",
            "Neutral is an uncertainty/abstention output below a probability threshold, not a trained third class.",
        ],
    }
    (RESULTS_DIR / "metrics.json").write_text(
        json.dumps(json_safe(report_data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    metadata = {
        "selected_model": selected_name,
        "model_path": "models/best_model.joblib",
        "labels": LABELS,
        "neutral_uncertainty_threshold": NEUTRAL_THRESHOLD,
        "input_preprocessing": "src.text_utils.normalize_text",
        "feature_count": feature_count,
    }
    (MODELS_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    make_model_comparison_chart(model_results)
    make_language_chart(model_results)
    make_confusion_chart(y_test, selected_predictions, selected_name)
    make_architecture_chart()
    print(json.dumps(json_safe(report_data), ensure_ascii=False, indent=2))
    print(f"Saved model: {MODELS_DIR / 'best_model.joblib'}")


if __name__ == "__main__":
    main()

