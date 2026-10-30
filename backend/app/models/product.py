from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_code = Column(String(32), unique=True, index=True, nullable=False)  # PRD-MOTOR-001
    name = Column(String(100), nullable=False)
    line_of_business = Column(String(50), nullable=False)  # MOTOR, HOME, HEALTH
    description = Column(Text, nullable=False)
    min_coverage_limit = Column(Numeric(12, 2), nullable=False)
    max_coverage_limit = Column(Numeric(12, 2), nullable=False)
    min_applicant_age = Column(Integer, default=18, nullable=False)
    max_applicant_age = Column(Integer, default=85, nullable=False)
    base_premium = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    coverage_options = relationship("CoverageOption", back_populates="product", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="product")
    policies = relationship("Policy", back_populates="product")


class CoverageOption(Base, TimestampMixin):
    __tablename__ = "coverage_options"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)  # COV-COMPREHENSIVE
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    coverage_category = Column(String(50), default="CORE", nullable=False)  # CORE, OPTIONAL, ADD_ON
    default_limit = Column(Numeric(12, 2), nullable=False)
    min_limit = Column(Numeric(12, 2), nullable=False)
    max_limit = Column(Numeric(12, 2), nullable=False)
    premium_multiplier = Column(Numeric(6, 4), default=0.15, nullable=False)
    deductible_options = Column(JSON, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="coverage_options")
