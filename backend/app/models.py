import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    source_type: Mapped[str] = mapped_column(String(40))
    owner: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="connected")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    checks: Mapped[list["QualityCheck"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class CheckStatus(str, enum.Enum):
    passed = "passed"
    failed = "failed"
    running = "running"
    pending = "pending"


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    check_type: Mapped[str] = mapped_column(String(50))
    column_name: Mapped[str] = mapped_column(String(120), default="")
    threshold: Mapped[float] = mapped_column(default=95.0)
    status: Mapped[CheckStatus] = mapped_column(Enum(CheckStatus), default=CheckStatus.pending)

    dataset: Mapped[Dataset] = relationship(back_populates="checks")
    runs: Mapped[list["QualityRun"]] = relationship(back_populates="check", cascade="all, delete-orphan")


class QualityRun(Base):
    __tablename__ = "quality_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    check_id: Mapped[int] = mapped_column(ForeignKey("quality_checks.id", ondelete="CASCADE"))
    status: Mapped[CheckStatus] = mapped_column(Enum(CheckStatus))
    score: Mapped[float] = mapped_column(default=0.0)
    message: Mapped[str] = mapped_column(Text, default="")
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    check: Mapped[QualityCheck] = relationship(back_populates="runs")
