# Practical Project Report / تقرير المشروع العملي

## English executive summary

This project implements an offline Arabic-English customer-review sentiment
classifier. It prepares a reproducible dataset, normalizes both scripts,
extracts character 3-5-gram TF-IDF features, compares Logistic Regression with
Multinomial Naive Bayes, evaluates both models, saves the selected pipeline, and
provides command-line and web interfaces.

After duplicate removal, the dataset contains 6,262 records: 2,979 English
review sentences and 3,283 Arabic AFINN terms or phrases. The fixed stratified
hold-out set contains 1,253 records. Logistic Regression achieved 74.06%
accuracy and 73.53% macro F1, compared with 73.50% accuracy and 72.40% macro F1
for Multinomial Naive Bayes. Logistic Regression was therefore selected.

The selected model reached 83.05% accuracy on held-out English review sentences
and 65.91% on held-out Arabic lexicon records. This difference is expected
because the English records are complete natural reviews while the Arabic
records are translated lexicon terms. The delivered paper reports this
limitation rather than combining the two results without context.

## الملخص التنفيذي بالعربية

ينفذ المشروع نظاماً محلياً لتحليل مشاعر مراجعات العملاء بالعربية والإنجليزية.
يقوم النظام بتجهيز البيانات بصورة قابلة لإعادة التجربة، ثم يطبّع الحروف العربية
والإنجليزية، ويستخرج خصائص TF-IDF من المقاطع الحرفية بطول 3 إلى 5 أحرف، ويقارن
بين خوارزميتي الانحدار اللوجستي ونايف بايز متعددة الحدود.

بعد إزالة السجلات المكررة أصبحت البيانات 6,262 سجلاً: 2,979 جملة مراجعة
إنجليزية و3,283 مفردة أو عبارة عربية من معجم AFINN. بلغ حجم بيانات الاختبار
1,253 سجلاً. حقق الانحدار اللوجستي دقة 74.06% وMacro-F1 مقداره 73.53%، ولذلك
تم اختياره وحفظه للاستخدام في التطبيق.

وصلت دقة النموذج إلى 83.05% على جمل المراجعات الإنجليزية، وإلى 65.91% على
السجلات العربية المعجمية. هذه الأرقام ليست قابلة للمقارنة المباشرة لأن طبيعة
بيانات اللغتين مختلفة. المرحلة التالية المقترحة هي جمع مراجعات عربية حقيقية
ومجهولة الهوية، وخصوصاً باللهجة الفلسطينية، ثم وسمها يدوياً واستخدامها في
التدريب والاختبار.

## Requirements mapping / مطابقة متطلبات المساق

| Course requirement | Delivered evidence |
| --- | --- |
| Simple working AI system | Saved classifier, CLI, local bilingual web interface |
| Practical implementation | Data preparation, training, evaluation, prediction and tests |
| Real data | UCI English review sentences with DOI and CC BY 4.0 attribution |
| Arabic-English character | Arabic lexicon component, Arabic normalization and bilingual UI |
| Results-based paper | ICRE paper generated from `results/metrics.json` |
| Privacy | No personal identifiers are required; offline inference |
| Team submission | All three students are named in the project and paper |

## System workflow / آلية عمل النظام

1. Read public English review sentences and the Arabic AFINN file.
2. Remove empty and duplicate records.
3. Normalize Unicode, Arabic diacritics, letter variants, URLs and whitespace.
4. Split data with stratification across language and label.
5. Convert text to character n-gram TF-IDF vectors.
6. Train Logistic Regression and Multinomial Naive Bayes.
7. Compare hold-out and five-fold cross-validation results.
8. Save the best model and publish predictions, metrics and charts.
9. Accept Arabic or English input through the CLI or local web page.

## Reproducibility

The random seed is fixed at 42. Raw source files, preprocessing code, processed
CSV, model code, saved model, complete test predictions, metrics, and figures
are included. Re-running `python -m src.prepare_data` and
`python -m src.train` reconstructs the experiment.

## Ethical and technical limits

- The Arabic component is a translated lexicon, not a natural Arabic review
  corpus.
- Neutral is returned only when confidence is below 0.60; it is not a trained
  third class.
- Sarcasm, dialect, Arabizi, and complex negation remain difficult.
- Production use would require local validation, calibration, human review,
  drift monitoring, and an appeal path.

