"""Audit Service for Todo Chatbot Application
Consumes Kafka events and creates audit logs for compliance.
"""
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from dotenv import load_dotenv, find_dotenv
from sqlmodel import Session, select, func
from sqlalchemy import desc
import json

from .database import DatabaseManager
from .kafka_consumer import AuditKafkaConsumer
from .models import AuditLog


load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to handle startup and shutdown."""
    # Initialize database manager
    db_manager = DatabaseManager(DATABASE_URL)
    await db_manager.initialize()

    # Initialize Kafka consumer
    kafka_consumer = AuditKafkaConsumer(db_manager)
    await kafka_consumer.initialize()

    # Store in app state
    app.state.db_manager = db_manager
    app.state.kafka_consumer = kafka_consumer
    app.state.running = True

    # Start consuming in background
    consume_task = asyncio.create_task(kafka_consumer.start_consuming())

    yield

    # Shutdown
    app.state.running = False
    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        pass

    await kafka_consumer.stop_consuming()
    await db_manager.close()

    logger.info("Audit Service shut down")


app = FastAPI(
    title="Audit Service",
    description="Handles creating audit logs based on Kafka events for compliance",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def read_root():
    """Root endpoint for the audit service."""
    return {"message": "Audit Service for Todo Chatbot", "status": "running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audit-service",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/database")
async def database_health():
    """Database connectivity health check."""
    try:
        db_manager: DatabaseManager = app.state.db_manager

        # Test the database connection by executing a simple query using SQLModel
        with Session(db_manager.engine) as session:
            result = session.exec(select(1).limit(1)).first()

        return {
            "status": "healthy",
            "service": "audit-database",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "audit-database",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.get("/audit-logs")
async def get_audit_logs(limit: int = 100, offset: int = 0):
    """Retrieve audit logs with pagination."""
    try:
        db_manager: DatabaseManager = app.state.db_manager

        with Session(db_manager.engine) as session:
            # Get total count for pagination metadata
            count_statement = select(func.count()).select_from(AuditLog)
            count = session.exec(count_statement).one()

            # Get audit logs with pagination
            statement = select(AuditLog).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit)
            results = session.exec(statement).all()

        # Convert results to list of dicts
        audit_logs = []
        for result in results:
            audit_logs.append({
                'event_id': result.event_id,
                'event_type': result.event_type,
                'user_id': result.user_id,
                'entity_type': result.entity_type,
                'entity_id': result.entity_id,
                'operation': result.operation,
                'timestamp': result.timestamp,
                'details': json.loads(result.details) if result.details else {},
                'source': result.source
            })

        return {
            "audit_logs": audit_logs,
            "count": len(audit_logs),
            "total": count,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs: {str(e)}")


@app.get("/audit-logs/search")
async def search_audit_logs(
    user_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    operation: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Search audit logs with filters."""
    try:
        db_manager: DatabaseManager = app.state.db_manager

        with Session(db_manager.engine) as session:
            # Build filters once
            filters = []
            if user_id:
                filters.append(AuditLog.user_id == user_id)
            if entity_type:
                filters.append(AuditLog.entity_type == entity_type)
            if entity_id:
                filters.append(AuditLog.entity_id == entity_id)
            if operation:
                filters.append(AuditLog.operation == operation)
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)

            # Get total count
            count_statement = select(func.count()).select_from(AuditLog).where(*filters)
            total_count = session.exec(count_statement).one()

            # Get paginated results
            statement = select(AuditLog).where(*filters).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit)
            results = session.exec(statement).all()

        # Convert results to list of dicts
        audit_logs = [
            {
                'event_id': result.event_id,
                'event_type': result.event_type,
                'user_id': result.user_id,
                'entity_type': result.entity_type,
                'entity_id': result.entity_id,
                'operation': result.operation,
                'timestamp': result.timestamp,
                'details': json.loads(result.details) if result.details else {},
                'source': result.source
            }
            for result in results
        ]

        return {
            "audit_logs": audit_logs,
            "count": len(audit_logs),
            "total": total_count,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error searching audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching audit logs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
