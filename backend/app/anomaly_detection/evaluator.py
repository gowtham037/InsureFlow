import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.anomaly import AnomalyRecord


def evaluate_anomaly_metrics(
    db: Session,
    ground_truth_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates detected anomalies against independently loaded ground truth labels.
    Prefers data/runtime_exports/ground_truth.json if present from a runtime generation run,
    otherwise falls back to the canonical submission baseline data/ground_truth/ground_truth.json.
    """
    if ground_truth_path is None:
        if os.path.exists("data/runtime_exports/ground_truth.json"):
            ground_truth_path = "data/runtime_exports/ground_truth.json"
        else:
            ground_truth_path = "data/ground_truth/ground_truth.json"

    if not os.path.exists(ground_truth_path):
        return {
            "error": "Ground truth file not found. Please inject anomalies first.",
            "total_ground_truth": 0,
            "total_detected": 0,
            "true_positives": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "breakdown": {}
        }

    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truth_data: List[Dict[str, Any]] = json.load(f)

    detected_records = db.query(AnomalyRecord).all()

    # Ground truth keyed by (entity_id, issue_type)
    gt_map = {(gt["entity_id"], gt["issue_type"]): gt for gt in ground_truth_data}
    detected_map = {(d.entity_id, d.issue_type): d for d in detected_records}

    tp_keys = set(gt_map.keys()) & set(detected_map.keys())
    fp_keys = set(detected_map.keys()) - set(gt_map.keys())
    fn_keys = set(gt_map.keys()) - set(detected_map.keys())

    tp = len(tp_keys)
    fp = len(fp_keys)
    fn = len(fn_keys)

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 1.0
    f1 = round((2 * precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    # Per issue type breakdown
    all_issue_types = set([k[1] for k in gt_map.keys()] + [k[1] for k in detected_map.keys()])
    breakdown = {}
    for itype in all_issue_types:
        gt_sub = [k for k in gt_map.keys() if k[1] == itype]
        det_sub = [k for k in detected_map.keys() if k[1] == itype]
        tp_sub = len(set(gt_sub) & set(det_sub))
        fp_sub = len(set(det_sub) - set(gt_sub))
        fn_sub = len(set(gt_sub) - set(det_sub))
        prec_sub = round(tp_sub / (tp_sub + fp_sub), 4) if (tp_sub + fp_sub) > 0 else 1.0
        rec_sub = round(tp_sub / (tp_sub + fn_sub), 4) if (tp_sub + fn_sub) > 0 else 1.0
        f1_sub = round((2 * prec_sub * rec_sub) / (prec_sub + rec_sub), 4) if (prec_sub + rec_sub) > 0 else 0.0

        breakdown[itype] = {
            "ground_truth_count": len(gt_sub),
            "detected_count": len(det_sub),
            "true_positives": tp_sub,
            "false_positives": fp_sub,
            "false_negatives": fn_sub,
            "precision": prec_sub,
            "recall": rec_sub,
            "f1_score": f1_sub
        }

    return {
        "total_ground_truth": len(ground_truth_data),
        "total_detected": len(detected_records),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "breakdown": breakdown
    }
