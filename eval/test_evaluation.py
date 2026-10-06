import pytest
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support

def test_metrics_calculation():
    # Mock data for flagged claims
    # 1: flagged, 0: not flagged
    y_true = [1, 1, 1, 0, 0, 1, 0, 1, 0, 0]
    y_pred = [1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
    
    # Calculate precision, recall
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    
    # Target 0.6 kappa
    kappa = cohen_kappa_score(y_true, y_pred, weights='quadratic')
    
    assert precision > 0.0
    assert recall > 0.0
    assert kappa is not None
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, Kappa: {kappa:.2f}")

def compute_metrics(y_true, y_pred):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred, weights='quadratic')
    return {
        "precision": precision,
        "recall": recall,
        "kappa": kappa
    }
