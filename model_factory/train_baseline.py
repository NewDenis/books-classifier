from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import FunctionTransformer
from model_factory.text_preprocessing import text_cleanup_preprocessor
import os
import pandas as pd
from tqdm import tqdm


STOPWORDS = [
    "а",
    "более",
    "бы",
    "был",
    "была",
    "были",
    "было",
    "быть",
    "в",
    "вам",
    "вас",
    "весь",
    "во",
    "вот",
    "все",
    "всего",
    "всех",
    "вы",
    "да",
    "для",
    "даже",
    "его",
    "ее",
    "если",
    "есть",
    "еще",
    "же",
    "за",
    "здесь",
    "и",
    "из",
    "или",
    "им",
    "их",
    "к",
    "как",
    "кто",
    "ко",
    "ли",
    "либо",
    "мне",
    "может",
    "мы",
    "на",
    "надо",
    "наш",
    "него",
    "нее",
    "ни",
    "них",
    "но",
    "ну",
    "о",
    "об",
    "однако",
    "он",
    "она",
    "они",
    "оно",
    "от",
    "очень",
    "по",
    "под",
    "при",
    "с",
    "со",
    "так",
    "также",
    "такой",
    "там",
    "те",
    "тем",
    "то",
    "того",
    "тоже",
    "той",
    "только",
    "том",
    "ты",
    "у",
    "уже",
    "хотя",
    "чего",
    "чей",
    "чем",
    "что",
    "чтобы",
    "чье",
    "чья",
    "эта",
    "эти",
    "это",
    "я",
    "что",
    "делать",
    "если",
    "какой",
    "для",
    "нужно",
    "какие",
    "можно",
    "изза",
    "из-за",
    "не",
    "все",
]


def train_baseline(tfidf, data_path, frac):
    raw_data_path = os.path.join(data_path, "datasets", "raw")
    train_data = []
    for file_name in tqdm(os.listdir(raw_data_path)):
        data = pd.read_parquet(
            os.path.join(raw_data_path, file_name), columns=["text", "cls1"]
        )
        train_data.append(data)
        break
    train_data = pd.concat(train_data, ignore_index=True)
    if frac < 1.0:
        splitter = StratifiedShuffleSplit(1, train_size=frac)
        for train_index, _ in splitter.split(
            train_data["text"], train_data["cls1"]
        ):
            train_data = (
                train_data.iloc[train_index].reset_index(drop=True).copy()
            )
    else:
        train_data.sample(frac=frac)
    vect_kwargs = {
        "stop_words": STOPWORDS,
        "max_features": 50_000,
        "ngram_range": (1, 3),
    }
    pipeline = Pipeline(
        [
            (
                "preprocessor",
                FunctionTransformer(
                    lambda x: [text_cleanup_preprocessor(text) for text in x]
                ),
            ),
            (
                "vectorizer",
                (TfidfVectorizer if tfidf else CountVectorizer)(**vect_kwargs),
            ),
            (
                "classifier",
                LogisticRegression(
                    verbose=1, class_weight="balanced", n_jobs=-1
                ),
            ),
        ]
    )
    return pipeline.fit(data["text"], data["cls1"])
