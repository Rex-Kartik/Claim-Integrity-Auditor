import pytest

def compute_metrics(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    total = len(y_true)
    po = (tp + tn) / total if total > 0 else 0
    pe = ((tp + fn) * (tp + fp) + (fp + tn) * (fn + tn)) / (total * total) if total > 0 else 0
    kappa = (po - pe) / (1 - pe) if (1 - pe) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "kappa": kappa
    }

def test_metrics_calculation():
    # Mock data for flagged claims
    y_true = [1, 1, 1, 0, 0, 1, 0, 1, 0, 0]
    y_pred = [1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
    
    metrics = compute_metrics(y_true, y_pred)
    
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
    assert metrics["kappa"] is not None
    print(f"Precision: {metrics['precision']:.2f}, Recall: {metrics['recall']:.2f}, Kappa: {metrics['kappa']:.2f}")

