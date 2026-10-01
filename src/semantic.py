from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import joblib
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


@dataclass
class SemanticEncoder:
    max_features: int = 5000
    n_components: int = 32
    random_state: int = 42

    def __post_init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1,
        )
        self.svd = None
        self._fitted = False

    def fit(self, texts: Iterable[str]):
        texts = [str(x or "") for x in texts]
        X = self.vectorizer.fit_transform(texts)
        max_comp = min(self.n_components, max(2, X.shape[0]-1), max(2, X.shape[1]-1))
        if X.shape[0] > 2 and X.shape[1] > 2:
            self.svd = TruncatedSVD(n_components=max_comp, random_state=self.random_state)
            Z = self.svd.fit_transform(X)
        else:
            Z = X.toarray()
        self._fitted = True
        return normalize(Z)

    def transform(self, texts: Iterable[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("fit first")
        X = self.vectorizer.transform([str(x or "") for x in texts])
        Z = self.svd.transform(X) if self.svd is not None else X.toarray()
        return normalize(Z)

    def save(self, path):
        joblib.dump(self, path)
