from transformers import pipeline

pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# revision pins the exact commit so a re-pull can't silently fetch different weights
pipeline(
    "translation_en_to_fr",
    model="Helsinki-NLP/opus-mt-en-fr",
    revision="dd7f6540a7a48a7f4db59e5c0b9c42c8eea67f18",
)
