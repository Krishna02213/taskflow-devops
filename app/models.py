from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, index=True)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=current_utc_time)


class TaskCreate(TaskBase):
    pass


class TaskPublic(TaskBase):
    id: int
    created_at: datetime


class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None