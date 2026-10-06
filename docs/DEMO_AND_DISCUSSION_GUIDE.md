# Demo and Discussion Guide / دليل العرض والمناقشة

## Five-minute demonstration

1. Open a terminal in the project folder.
2. Run `python web_app.py` and open `http://127.0.0.1:8000`.
3. Test a positive English review: `The product is excellent and easy to use.`
4. Test a negative English review: `This is terrible and a waste of money.`
5. Test Arabic positive text: `الخدمة ممتازة وسريعة وأنا سعيد جداً`.
6. Test Arabic negative text: `الخدمة سيئة ومخيبة للآمال`.
7. Open `results/model_comparison.png` and explain why Logistic Regression was
   selected.
8. Open `results/confusion_matrix.png` and explain false positives and false
   negatives.
9. End with the limitation: the Arabic evaluation is lexicon-based and the next
   step is an annotated Palestinian Arabic review corpus.

## Suggested team split / تقسيم مقترح للفريق

- Student 1: dataset, preprocessing, and privacy.
- Student 2: TF-IDF, model training, and evaluation metrics.
- Student 3: interfaces, testing, results, and paper integration.

Every member should still understand the full pipeline because the team will be
discussed together.

## Likely questions and short answers

**Why character n-grams?**  They support Arabic and English without separate
tokenizers and capture subword patterns and spelling variation.

**Why Logistic Regression?**  It achieved the best hold-out macro F1 (73.53%)
and the best English result while remaining fast and interpretable.

**Is neutral a real class?**  No. The trained labels are positive and negative.
Neutral/uncertain is an abstention when maximum probability is below 0.60.

**Why is Arabic performance lower?**  The Arabic data are translated sentiment
terms rather than complete annotated reviews, and Arabic morphology and dialect
increase variation.

**How was privacy protected?**  The system does not need names or direct
identifiers, all inference is local, and new data should be anonymized.

**What would improve the project most?**  A large manually annotated Arabic and
mixed-language customer-review dataset from the target domain.

