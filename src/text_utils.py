"""Text normalization and lightweight language detection utilities."""

from __future__ import annotations

import re
import unicodedata


ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
ARABIC_DIACRITICS_RE = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]"
)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
WHITESPACE_RE = re.compile(r"\s+")
NON_TEXT_RE = re.compile(r"[^0-9A-Za-z\u0600-\u06FF\s!?']+")


def detect_language(text: str) -> str:
    """Return ``ar``, ``en``, or ``mixed`` based on Unicode characters."""
    text = text or ""
    arabic_count = len(ARABIC_RE.findall(text))
    latin_count = len(re.findall(r"[A-Za-z]", text))
    if arabic_count and latin_count:
        total = arabic_count + latin_count
        if arabic_count / total >= 0.80:
            return "ar"
        if latin_count / total >= 0.80:
            return "en"
        return "mixed"
    if arabic_count:
        return "ar"
    return "en"


def normalize_text(text: str) -> str:
    """Normalize Arabic and English while preserving sentiment-bearing text."""
    text = unicodedata.normalize("NFKC", str(text or ""))
    text = URL_RE.sub(" URL ", text)
    text = EMAIL_RE.sub(" EMAIL ", text)
    text = text.replace("ـ", "")
    text = ARABIC_DIACRITICS_RE.sub("", text)
    text = (
        text.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ٱ", "ا")
        .replace("ى", "ي")
    )
    text = text.lower()
    text = NON_TEXT_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()

