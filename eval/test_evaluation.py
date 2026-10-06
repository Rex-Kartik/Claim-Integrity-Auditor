import pytest
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support

def compute_metrics(y_true, y_pred):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred, weights='quadratic')
    return {
        "precision": precision,
        "recall": recall,
        "kappa": kappa
    }

def test_metrics_calculation():
    # Mock data for flagged claims
    # 1: flagged, 0: not flagged
    y_true = [1, 1, 1, 0, 0, 1, 0, 1, 0, 0]
    y_pred = [1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
    
    metrics = compute_metrics(y_true, y_pred)
    
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
    assert metrics["kappa"] is not None
    print(f"Precision: {metrics['precision']:.2f}, Recall: {metrics['recall']:.2f}, Kappa: {metrics['kappa']:.2f}")


