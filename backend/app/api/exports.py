import os
import io
import zipfile
from fastapi import APIRouter, HTTPException, Query, Response
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


def resolve_export_file(filename: str) -> Optional[str]:
    """
    Checks data/runtime_exports/ first (newest runtime generation),
    and falls back to data/exports/ (canonical committed submission baseline).
    """
    runtime_path = os.path.join("data/runtime_exports", filename)
    if os.path.exists(runtime_path):
        return runtime_path
    baseline_path = os.path.join("data/exports", filename)
    if os.path.exists(baseline_path):
        return baseline_path
    return None


@router.get("")
def list_exports():
    """
    Returns a catalog of all generated datasets, formats, file sizes, and download links.
    """
    datasets = []
    for name in VALID_DATASETS:
        csv_path = resolve_export_file(f"{name}.csv")
        json_path = resolve_export_file(f"{name}.json")
        datasets.append({
            "name": name,
            "has_csv": csv_path is not None,
            "csv_size_bytes": os.path.getsize(csv_path) if csv_path else 0,
            "has_json": json_path is not None,
            "json_size_bytes": os.path.getsize(json_path) if json_path else 0,
            "csv_url": f"/api/exports/{name}?format=csv",
            "json_url": f"/api/exports/{name}?format=json"
        })
    sql_path = resolve_export_file("seed_data.sql")
    return {
        "datasets": datasets,
        "has_sql_seed": sql_path is not None,
        "sql_seed_url": "/api/exports/sql-seed",
        "zip_bundle_url": "/api/exports/bundle?format=csv",
        "export_source": "runtime_exports" if os.path.exists("data/runtime_exports") and os.listdir("data/runtime_exports") else "baseline_exports"
    }


@router.get("/bundle")
@router.get("/bundle.zip")
@router.get("/insureflow_{format}_all_datasets.zip")
def export_bundle_zip(format: str = "csv"):
    """
    Creates and streams an in-memory ZIP archive containing all generated datasets.
    """
    clean_format = format.lower().strip()
    if clean_format not in ["csv", "json", "all"]:
        clean_format = "csv"

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for name in VALID_DATASETS:
            if clean_format in ["csv", "all"]:
                csv_path = resolve_export_file(f"{name}.csv")
                if csv_path:
                    zip_file.write(csv_path, arcname=f"{name}.csv")
            if clean_format in ["json", "all"]:
                json_path = resolve_export_file(f"{name}.json")
                if json_path:
                    zip_file.write(json_path, arcname=f"{name}.json")
        sql_path = resolve_export_file("seed_data.sql")
        if sql_path:
            zip_file.write(sql_path, arcname="seed_data.sql")

    zip_buffer.seek(0)
    filename = f"insureflow_{clean_format}_all_datasets.zip"
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{filename}',
            "Content-Type": "application/zip",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/sql-seed")
@router.get("/seed_data.sql")
def export_sql_seed():
    file_path = resolve_export_file("seed_data.sql")
    if not file_path:
        raise HTTPException(status_code=404, detail="SQL seed data script not found. Please generate dataset first.")
    return FileResponse(
        file_path,
        media_type="application/sql",
        filename="seed_data.sql",
        headers={
            "Content-Disposition": 'attachment; filename="seed_data.sql"; filename*=UTF-8\'\'seed_data.sql',
            "Content-Type": "application/sql; charset=utf-8",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/{dataset_name}")
def export_dataset(
    dataset_name: str,
    format: Optional[str] = Query(None)
):
    """
    Downloads any of the 15 insurance datasets in CSV or JSON format.
    Accepts both:
      - /api/exports/applicants.csv
      - /api/exports/applicants.json
      - /api/exports/applicants?format=csv
      - /api/exports/seed_data.sql
      - /api/exports/bundle.zip
    """
    raw_name = dataset_name.strip()
    if raw_name in ["seed_data.sql", "sql-seed", "seed.sql"]:
        return export_sql_seed()
    if raw_name in ["bundle.zip", "bundle", "all.zip"]:
        return export_bundle_zip(format=format or "csv")

    determined_format = "csv"
    if raw_name.endswith(".csv"):
        determined_format = "csv"
        raw_name = raw_name[:-4]
    elif raw_name.endswith(".json"):
        determined_format = "json"
        raw_name = raw_name[:-5]
    elif format and format.lower() in ["csv", "json"]:
        determined_format = format.lower()

    clean_name = raw_name.lower().replace("-", "_")
    if clean_name not in VALID_DATASETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dataset '{dataset_name}'. Allowed: {VALID_DATASETS}"
        )

    ext = determined_format
    media_type = "application/json" if ext == "json" else "text/csv"
    file_path = resolve_export_file(f"{clean_name}.{ext}")

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset file '{clean_name}.{ext}' not found. Please generate dataset first."
        )

    out_filename = f"{clean_name}.{ext}"
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=out_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{out_filename}"; filename*=UTF-8\'\'{out_filename}',
            "Content-Type": f"{media_type}; charset=utf-8",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
