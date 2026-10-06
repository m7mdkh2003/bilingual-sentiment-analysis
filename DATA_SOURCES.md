# Data Sources and Ethical Use / مصادر البيانات والاستخدام الأخلاقي

## English review component

The 3,000 English sentences are from the UCI Machine Learning Repository's
**Sentiment Labelled Sentences** dataset (DOI: `10.24432/C57604`). It contains
1,000 sentences from each of Amazon, IMDb, and Yelp, with 500 positive and 500
negative sentences per source. UCI publishes the dataset under CC BY 4.0.

Dataset page: https://archive.ics.uci.edu/dataset/331/sentiment+labelled+sentences

## Arabic component

The Arabic component consists of non-zero Arabic entries from the translated
AFINN-165 word list distributed by `multilang-sentiment` under the MIT license.
Each term keeps the sign of its lexicon score as a positive or negative label.

Repository: https://github.com/marcellobarile/multilang-sentiment

Important limitation: these Arabic records are sentiment terms and short
phrases, not a natural corpus of complete customer reviews. The project reports
Arabic and English performance separately and does not represent the Arabic
lexicon score as full review-level validation.

## الخصوصية

المشروع لا يحتاج أسماء أشخاص أو أرقام هواتف أو عناوين. البيانات المستخدمة
نصوص عامة مجهولة الهوية، ويجب حذف أي معرّفات شخصية قبل إضافة بيانات جديدة.

