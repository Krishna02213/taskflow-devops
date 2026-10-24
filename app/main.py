from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow API",
    description="A task-management application for learning DevOps",
    version="0.1.0",
)


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