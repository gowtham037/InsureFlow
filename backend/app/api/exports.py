import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

router = APIRouter(prefix="/exports", tags=["Exports"])

VALID_DATASETS = [
    "applicants",
    "insured_assets",
    "products",
    "coverage_options",
    "risk_factors",
    "quotes",
    "quote_coverages",
    "underwriting_decisions",
    "policies",
    "policy_coverages",
    "endorsements",
    "renewals",
    "policy_events",
    "anomaly_records",
    "ground_truth"
]


@router.get("")
def list_exports():
    """
    Returns a catalog of all generated datasets, formats, file sizes, and download links.
    """
    export_dir = "data/exports"
    datasets = []
    for name in VALID_DATASETS:
        csv_path = os.path.join(export_dir, f"{name}.csv")
        json_path = os.path.join(export_dir, f"{name}.json")
        datasets.append({
            "name": name,
            "has_csv": os.path.exists(csv_path),
            "csv_size_bytes": os.path.getsize(csv_path) if os.path.exists(csv_path) else 0,
            "has_json": os.path.exists(json_path),
            "json_size_bytes": os.path.getsize(json_path) if os.path.exists(json_path) else 0,
            "csv_url": f"/api/exports/{name}?format=csv",
            "json_url": f"/api/exports/{name}?format=json"
        })
    sql_path = os.path.join(export_dir, "seed_data.sql")
    return {
        "datasets": datasets,
        "has_sql_seed": os.path.exists(sql_path),
        "sql_seed_url": "/api/exports/sql-seed"
    }


@router.get("/sql-seed")
def export_sql_seed():
    file_path = "data/exports/seed_data.sql"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="SQL seed data script not found. Please generate dataset first.")
    return FileResponse(file_path, media_type="application/sql", filename="seed_data.sql")


@router.get("/{dataset_name}")
def export_dataset(
    dataset_name: str,
    format: str = Query("csv", pattern="^(csv|json)$")
):
    """
    Downloads any of the 15 insurance datasets in CSV or JSON format.
    """
    clean_name = dataset_name.lower().replace("-", "_")
    if clean_name not in VALID_DATASETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dataset '{dataset_name}'. Allowed: {VALID_DATASETS}"
        )

    ext = "json" if format == "json" else "csv"
    media_type = "application/json" if format == "json" else "text/csv"
    file_path = os.path.join("data/exports", f"{clean_name}.{ext}")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset file '{clean_name}.{ext}' not found. Please generate dataset first."
        )

    return FileResponse(file_path, media_type=media_type, filename=f"{clean_name}.{ext}")
