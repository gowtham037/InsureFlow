from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class AnomalyResponse(BaseModel):
    id: int
    business_id: str
    entity_type: str
    entity_id: str
    issue_type: str
    severity: str
    description: str
    expected_outcome: str
    actual_detected_outcome: str
    is_detected: bool
    ground_truth_label: bool
    detection_rule: str
    detection_explanation: str
    detected_at: datetime

    class Config:
        from_attributes = True


class AnomalySummaryResponse(BaseModel):
    total_anomalies: int
    severity_breakdown: Dict[str, int]
    issue_type_breakdown: Dict[str, int]
    evaluation_metrics: Dict[str, Any]
