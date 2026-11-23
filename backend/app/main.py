import random
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .integrations import get_adapter
from .models import CheckStatus, Dataset, QualityCheck, QualityRun
from .schemas import CheckCreate, CheckRead, DatasetCreate, DatasetRead, RunRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if db.scalar(select(func.count(Dataset.id))) == 0:
            db.add_all([
                Dataset(name="Customer 360", source_type="PostgreSQL", owner="Data Platform", description="Unified customer profile"),
                Dataset(name="Revenue Warehouse", source_type="Snowflake", owner="Finance Analytics", description="Monthly revenue data"),
                Dataset(name="Support Tickets", source_type="MySQL", owner="Customer Experience", description="Support activity history"),
            ])
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="Data Quality Hub API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}


@app.post("/api/datasets", response_model=DatasetRead, status_code=201)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Dataset).where(Dataset.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="A dataset with this name already exists")
    dataset = Dataset(**payload.model_dump())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@app.get("/api/datasets", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)):
    return db.scalars(select(Dataset).order_by(Dataset.created_at.desc())).all()


@app.get("/api/datasets/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@app.post("/api/checks", response_model=CheckRead, status_code=201)
def create_check(payload: CheckCreate, db: Session = Depends(get_db)):
    if not db.get(Dataset, payload.dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    check = QualityCheck(**payload.model_dump())
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@app.get("/api/checks", response_model=list[CheckRead])
def list_checks(dataset_id: int | None = None, db: Session = Depends(get_db)):
    statement = select(QualityCheck)
    if dataset_id:
        statement = statement.where(QualityCheck.dataset_id == dataset_id)
    return db.scalars(statement.order_by(QualityCheck.id.desc())).all()


@app.post("/api/checks/{check_id}/run", response_model=RunRead)
def run_check(check_id: int, db: Session = Depends(get_db)):
    check = db.get(QualityCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Quality check not found")

    score = round(random.uniform(check.threshold - 8, 100), 1)
    status = CheckStatus.passed if score >= check.threshold else CheckStatus.failed
    run = QualityRun(
        check_id=check.id,
        status=status,
        score=score,
        message=f"{check.name} scored {score}% against a {check.threshold}% threshold",
    )
    check.status = status
    db.add(run)
    db.commit()
    db.refresh(run)
    return {
        "id": run.id,
        "check_id": run.check_id,
        "check_name": check.name,
        "dataset_name": check.dataset.name,
        "status": run.status,
        "score": run.score,
        "message": run.message,
        "executed_at": run.executed_at,
    }


@app.get("/api/runs", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)):
    statement = (
        select(QualityRun)
        .join(QualityCheck)
        .join(Dataset)
        .order_by(QualityRun.executed_at.desc())
    )
    runs = db.scalars(statement).all()
    return [
        {
            "id": run.id,
            "check_id": run.check_id,
            "check_name": run.check.name,
            "dataset_name": run.check.dataset.name,
            "status": run.status,
            "score": run.score,
            "message": run.message,
            "executed_at": run.executed_at,
        }
        for run in runs
    ]


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    dataset_count = db.scalar(select(func.count(Dataset.id))) or 0
    check_count = db.scalar(select(func.count(QualityCheck.id))) or 0
    passed = db.scalar(select(func.count(QualityRun.id)).where(QualityRun.status == CheckStatus.passed)) or 0
    failed = db.scalar(select(func.count(QualityRun.id)).where(QualityRun.status == CheckStatus.failed)) or 0
    average = db.scalar(select(func.avg(QualityRun.score))) or 0
    return {
        "dataset_count": dataset_count,
        "check_count": check_count,
        "passed": passed,
        "failed": failed,
        "average_score": round(float(average), 1),
    }


@app.post("/api/integrations/{provider}/sync")
async def sync_integration(provider: str):
    try:
        adapter = get_adapter(provider)
        return await adapter.sync()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
