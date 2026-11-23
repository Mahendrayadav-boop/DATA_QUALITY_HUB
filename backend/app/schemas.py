from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from .models import CheckStatus


class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    source_type: str = Field(min_length=2, max_length=40)
    owner: str = Field(min_length=2, max_length=120)
    description: str = ""


class DatasetRead(DatasetCreate):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckCreate(BaseModel):
    dataset_id: int
    name: str = Field(min_length=2, max_length=120)
    check_type: str = Field(min_length=2, max_length=50)
    column_name: str = ""
    threshold: float = Field(default=95.0, ge=0, le=100)


class CheckRead(CheckCreate):
    id: int
    status: CheckStatus

    model_config = ConfigDict(from_attributes=True)


class RunRead(BaseModel):
    id: int
    check_id: int
    check_name: str
    dataset_name: str
    status: CheckStatus
    score: float
    message: str
    executed_at: datetime
