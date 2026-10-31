import pytest
from datetime import date
from backend.app.database import SessionLocal
from backend.app.models.base import RecordSource
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.quote import Quote
from backend.app.models.policy import Policy
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.models.audit import AuditLog
from backend.app.data_generator.generator import generate_dataset
from backend.app.validation.validator import run_comprehensive_validation
from backend.app.anomaly_detection.detector import run_anomaly_detection


def test_user_data_preservation_across_generation():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.database import Base
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    db = TestSession()
    try:

        # 1. Create a user applicant manually with RecordSource.USER
        test_app = Applicant(
            business_id="APP-USER-999001",
            first_name="ManualTestUser",
            last_name="PreservationCheck",
            email="manual.user.preservation@example.com",
            phone="5551234567",
            date_of_birth=date(1990, 5, 15),
            age=36,
            gender="FEMALE",
            address_line="123 Protected St",
            city="Seattle",
            state="WA",
            postal_code="98101",
            country="USA",
            annual_income=95000.0,
            credit_score=750,
            occupation="Engineer",
            employment_status="EMPLOYED",
            claims_count_5yr=0,
            record_source=RecordSource.USER
        )
        db.add(test_app)

        # Also add an audit log
        audit_entry = AuditLog(
            entity_type="APPLICANT",
            entity_id="APP-USER-999001",
            action="CREATE",
            actor="Manual User Admin",
            new_values={"email": "manual.user.preservation@example.com"}
        )
        db.add(audit_entry)
        db.commit()

        user_app_id = test_app.id
        audit_id = audit_entry.id

        # 2. Trigger dataset generation (starter mode)
        res = generate_dataset(mode="starter", seed=20261022, db=db)
        assert res["counts"]["applicants"] == 300
        assert res["counts"]["quotes"] == 400
        assert res["counts"]["policies"] == 200

        # 3. Verify the manually created applicant still exists!
        found_app = db.query(Applicant).filter(Applicant.business_id == "APP-USER-999001").first()
        assert found_app is not None, "Manual applicant was deleted by synthetic generation!"
        assert found_app.first_name == "ManualTestUser"
        assert found_app.record_source == RecordSource.USER

        # Verify audit log was NOT deleted
        found_audit = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
        assert found_audit is not None, "AuditLog was deleted by synthetic generation!"

        # 4. Attach user asset, quote, and policy to this user applicant
        user_asset = InsuredAsset(
            business_id="AST-USER-999001",
            applicant_id=found_app.id,
            asset_type="MOTOR_VEHICLE",
            identifier="ID-MOT-999001",
            asset_value=35000.0,
            year_built_or_manufactured=2022,
            make_model="Tesla Model 3",
            location_tier="TIER_1",
            details={"vin": "1HGCR2F8000999001"},
            record_source=RecordSource.USER
        )
        db.add(user_asset)
        db.flush()

        from datetime import datetime, timedelta
        from backend.app.models.product import Product
        from backend.app.rules.pricing import calculate_premium
        motor_prod = db.query(Product).filter(Product.line_of_business == "MOTOR").first()

        prem, _, _ = calculate_premium(
            product_line=motor_prod.line_of_business,
            base_premium=float(motor_prod.base_premium),
            applicant_age=found_app.age,
            asset_value=float(user_asset.asset_value),
            asset_year=user_asset.year_built_or_manufactured,
            location_tier=user_asset.location_tier,
            claims_count=found_app.claims_count_5yr,
            coverage_amount=35000.0,
            deductible=500.0,
            asset_details=user_asset.details or {}
        )

        user_quote = Quote(
            business_id="QTE-USER-999001",
            applicant_id=found_app.id,
            asset_id=user_asset.id,
            product_id=motor_prod.id,
            coverage_amount=35000.0,
            deductible=500.0,
            status="ACCEPTED",
            risk_score=20,
            risk_tier="LOW",
            base_premium=float(motor_prod.base_premium),
            final_premium=prem,
            eligibility_passed=True,
            customer_accepted=True,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_baseline=False,
            record_source=RecordSource.USER
        )
        db.add(user_quote)
        db.flush()

        user_policy = Policy(
            business_id="POL-USER-999001",
            quote_id=user_quote.id,
            applicant_id=found_app.id,
            asset_id=user_asset.id,
            product_id=motor_prod.id,
            status="ACTIVE",
            coverage_amount=35000.0,
            deductible=500.0,
            annual_premium=prem,
            payment_status="PAID",
            customer_accepted=True,
            effective_date=date(2026, 2, 1),
            expiration_date=date(2027, 2, 1),
            is_baseline=False,
            record_source=RecordSource.USER
        )
        db.add(user_policy)
        db.commit()

        # 5. Regenerate synthetic data again
        res2 = generate_dataset(mode="starter", seed=20261022, db=db)
        assert res2["counts"]["applicants"] == 300
        assert res2["counts"]["quotes"] == 400
        assert res2["counts"]["policies"] == 200

        # 6. Verify all user entities survived intact with relationships preserved!
        surviving_app = db.query(Applicant).filter(Applicant.business_id == "APP-USER-999001").first()
        assert surviving_app is not None
        surviving_asset = db.query(InsuredAsset).filter(InsuredAsset.business_id == "AST-USER-999001").first()
        assert surviving_asset is not None
        assert surviving_asset.applicant_id == surviving_app.id
        surviving_quote = db.query(Quote).filter(Quote.business_id == "QTE-USER-999001").first()
        assert surviving_quote is not None
        assert surviving_quote.applicant_id == surviving_app.id
        surviving_pol = db.query(Policy).filter(Policy.business_id == "POL-USER-999001").first()
        assert surviving_pol is not None
        assert surviving_pol.applicant_id == surviving_app.id
        assert surviving_pol.quote_id == surviving_quote.id

        # 7. Check database integrity report
        report = run_comprehensive_validation(db)
        assert report["foreign_key_errors_count"] == 0
        assert report["duplicate_records_count"] == 0

    finally:
        # Guarantee cleanup of test records and refresh anomaly detections
        db.query(Policy).filter(Policy.business_id == "POL-USER-999001").delete()
        db.query(Quote).filter(Quote.business_id == "QTE-USER-999001").delete()
        db.query(InsuredAsset).filter(InsuredAsset.business_id == "AST-USER-999001").delete()
        db.query(Applicant).filter(Applicant.business_id == "APP-USER-999001").delete()
        db.query(AuditLog).filter(AuditLog.entity_id == "APP-USER-999001").delete()
        db.commit()
        run_anomaly_detection(db)
        db.close()
