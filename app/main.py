from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlmodel import Session, select

from app.database import create_db_and_tables, get_session
from app.models import Task, TaskCreate, TaskPublic, TaskUpdate


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title="TaskFlow API",
    description="A task-management application for learning DevOps",
    version="0.1.0",
    lifespan=lifespan,
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def root():
    return {
        "application": "TaskFlow",
        "message": "TaskFlow API is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.get("/info")
def application_info():
    return {
        "name": "TaskFlow API",
        "version": "0.1.0",
        "environment": "development",
    }


@app.post(
    "/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate, session: SessionDep):
    database_task = Task.model_validate(task)

    session.add(database_task)
    session.commit()
    session.refresh(database_task)

    return database_task


@app.get("/tasks", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    statement = select(Task).order_by(Task.id).offset(offset).limit(limit)
    return session.exec(statement).all()


@app.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_data)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)