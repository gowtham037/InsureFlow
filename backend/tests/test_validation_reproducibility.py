import pytest
from backend.app.database import SessionLocal
from backend.app.validation.validator import run_comprehensive_validation
from backend.app.data_generator.generator import generate_dataset


def test_foreign_key_and_database_integrity():
    db = SessionLocal()
    report = run_comprehensive_validation(db)
    db.close()

    assert report["foreign_key_errors_count"] == 0
    assert report["duplicate_records_count"] == 0
    assert report["validation_pass_rate_pct"] >= 99.0


def test_deterministic_reproducibility():
    # Running generation with fixed seed should produce consistent counts in isolated session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.database import Base

    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)

    db1 = TestSession()
    res1 = generate_dataset(mode="starter", seed=20261022, db=db1)
    c1 = res1["counts"]
    db1.close()

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db2 = TestSession()
    res2 = generate_dataset(mode="starter", seed=20261022, db=db2)
    c2 = res2["counts"]
    db2.close()

    assert c1 == c2
    assert c1["products"] == 3
    assert c1["applicants"] == 300
    assert c1["quotes"] == 400
    assert c1["policies"] == 200
