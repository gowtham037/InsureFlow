import pytest
from backend.app.database import SessionLocal
from backend.app.models.anomaly import AnomalyRecord
from backend.app.anomaly_detection.detector import run_anomaly_detection
from backend.app.anomaly_detection.evaluator import evaluate_anomaly_metrics


def test_anomaly_detection_identifies_all_five_types():
    db = SessionLocal()
    detected = run_anomaly_detection(db)
    detected_types = set(d.issue_type for d in detected)

    required_types = {
        "ISSUANCE_WITHOUT_ACCEPTANCE",
        "PREMIUM_FORMULA_MISMATCH",
        "ENDORSEMENT_LIMIT_EXCEEDED",
        "RENEWAL_ON_CANCELLED_POLICY",
        "OVERLAPPING_POLICY_PERIOD"
    }

    assert required_types.issubset(detected_types), f"Missing anomaly types: {required_types - detected_types}"
    db.close()


def test_anomaly_evaluation_metrics_precision_and_recall():
    db = SessionLocal()
    metrics = evaluate_anomaly_metrics(db)
    db.close()

    assert metrics["total_ground_truth"] >= 5
    assert metrics["true_positives"] >= 5
    assert metrics["false_negatives"] == 0
    assert metrics["recall"] == 1.0  # 100% recall on injected scenarios
    assert metrics["precision"] >= 0.90  # High precision
    assert metrics["f1_score"] >= 0.90
