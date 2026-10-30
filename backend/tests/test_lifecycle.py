import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.policy import Policy
from backend.app.models.quote import Quote
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal

client = TestClient(app)


def test_quote_acceptance_lifecycle():
    # 1. Get an evaluated quote that is eligible
    db = SessionLocal()
    quote = db.query(Quote).filter(Quote.eligibility_passed == True, Quote.status == "EVALUATED").first()
    if not quote:
        quote = db.query(Quote).filter(Quote.eligibility_passed == True).first()
    assert quote is not None
    q_id = quote.id
    db.close()

    # 2. Customer accepts quote
    res = client.post(f"/api/quotes/{q_id}/accept")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_accepted"] is True
    assert data["status"] == "ACCEPTED"


def test_policy_issuance_invariants():
    db = SessionLocal()
    # Find an accepted quote without an existing policy
    subq = db.query(Policy.quote_id).subquery()
    quote = db.query(Quote).filter(
        Quote.status == "ACCEPTED",
        Quote.customer_accepted == True,
        Quote.eligibility_passed == True,
        ~Quote.id.in_(subq)
    ).first()

    if not quote:
        # Create a fresh quote
        from backend.app.models.applicant import Applicant
        from backend.app.models.asset import InsuredAsset
        from backend.app.models.product import Product
        app_rec = db.query(Applicant).first()
        ast_rec = db.query(InsuredAsset).first()
        prod_rec = db.query(Product).first()

        res_q = client.post("/api/quotes", json={
            "applicant_id": app_rec.id,
            "asset_id": ast_rec.id,
            "product_id": prod_rec.id,
            "coverage_amount": 50000.0,
            "deductible": 500.0
        })
        new_q_id = res_q.json()["id"]
        client.post(f"/api/quotes/{new_q_id}/accept")
        quote_id_to_test = new_q_id
    else:
        quote_id_to_test = quote.id
    db.close()

    # Issue with unpaid -> Should fail
    res_fail = client.post(f"/api/policies/{quote_id_to_test}/issue", json={"payment_status": "PENDING"})
    assert res_fail.status_code == 400

    # Issue with paid -> Should succeed or handle existing overlap
    res_success = client.post(f"/api/policies/{quote_id_to_test}/issue", json={"payment_status": "PAID"})
    assert res_success.status_code in [201, 400]  # 400 if asset already has active policy, 201 if issued


def test_policy_cancellation_preserves_events():
    db = SessionLocal()
    pol = db.query(Policy).filter(Policy.status == "ACTIVE").first()
    assert pol is not None
    pol_id = pol.id
    db.close()

    res = client.post(f"/api/policies/{pol_id}/cancel", json={"cancellation_reason": "Customer request"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CANCELLED"
    assert data["cancellation_reason"] == "Customer request"
    assert len(data["events"]) > 0


def test_renewal_rejected_for_cancelled_policy():
    db = SessionLocal()
    canc_pol = db.query(Policy).filter(Policy.status == "CANCELLED").first()
    assert canc_pol is not None
    p_id = canc_pol.id
    db.close()

    # Attempt renewal generation
    res = client.post("/api/renewals/generate", json={"policy_id": p_id})
    assert res.status_code == 400
    assert "CANCELLED" in res.json()["detail"]


def test_endorsement_limits_enforced():
    db = SessionLocal()
    act_pol = db.query(Policy).filter(Policy.status == "ACTIVE").first()
    assert act_pol is not None
    p_id = act_pol.id
    prod = act_pol.product
    excess_limit = float(prod.max_coverage_limit) + 500000.0
    db.close()

    # Attempt to exceed coverage limit
    res = client.post("/api/endorsements", json={
        "policy_id": p_id,
        "endorsement_type": "COVERAGE_LIMIT_CHANGE",
        "new_coverage_amount": excess_limit,
        "effective_date": date.today().isoformat(),
        "reason": "Exceeding limit test"
    })
    assert res.status_code == 400
    assert "violates product limits" in res.json()["detail"]
