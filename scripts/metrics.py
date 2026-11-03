"""Classification metrics used by Turkish model evaluation."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def equal_error_rate(labels: np.ndarray, scores: np.ndarray) -> float:
    """Return the equal-error rate for positive-class scores."""
    false_positive_rate, true_positive_rate, _ = roc_curve(labels, scores)
    false_negative_rate = 1.0 - true_positive_rate
    difference = false_positive_rate - false_negative_rate
    exact = np.flatnonzero(np.isclose(difference, 0.0))
    if len(exact):
        return float(false_positive_rate[exact[0]])
    crossing = np.where(np.diff(np.sign(difference)))[0]
    if not len(crossing):
        return float(np.min(np.maximum(false_positive_rate, false_negative_rate)))
    index = crossing[0]
    return float((false_positive_rate[index] + false_negative_rate[index]) / 2.0)


def classification_metrics(labels: list[int], scores: list[float]) -> dict:
    """Calculate threshold and ranking metrics for binary predictions."""
    labels_array = np.asarray(labels, dtype=np.int64)
    scores_array = np.asarray(scores, dtype=np.float64)
    predictions = (scores_array >= 0.5).astype(np.int64)
    if set(labels_array.tolist()) != {0, 1}:
        raise ValueError("Metrics require both binary labels 0 and 1")
    return {
        "roc_auc": float(roc_auc_score(labels_array, scores_array)),
        "eer": equal_error_rate(labels_array, scores_array),
        "f1": float(f1_score(labels_array, predictions, zero_division=0)),
        "precision": float(precision_score(labels_array, predictions, zero_division=0)),
        "recall": float(recall_score(labels_array, predictions, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(labels_array, predictions)),
        "confusion_matrix": confusion_matrix(labels_array, predictions).tolist(),
    }
