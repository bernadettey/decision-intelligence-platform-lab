from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessUnit(Base):
    __tablename__ = "business_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)


class CostCentre(Base):
    __tablename__ = "cost_centres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    business_unit_id: Mapped[int] = mapped_column(ForeignKey("business_units.id"), nullable=False)

    business_unit: Mapped[BusinessUnit] = relationship()


class Actual(Base):
    __tablename__ = "actuals"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[Date] = mapped_column(Date, nullable=False)
    business_unit_id: Mapped[int] = mapped_column(ForeignKey("business_units.id"), nullable=False)
    cost_centre_id: Mapped[int] = mapped_column(ForeignKey("cost_centres.id"), nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    cogs: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    opex: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[Date] = mapped_column(Date, nullable=False)
    business_unit_id: Mapped[int] = mapped_column(ForeignKey("business_units.id"), nullable=False)
    cost_centre_id: Mapped[int] = mapped_column(ForeignKey("cost_centres.id"), nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    cogs: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    opex: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[Date] = mapped_column(Date, nullable=False)
    business_unit_id: Mapped[int] = mapped_column(ForeignKey("business_units.id"), nullable=False)
    cost_centre_id: Mapped[int] = mapped_column(ForeignKey("cost_centres.id"), nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    cogs: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    opex: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
