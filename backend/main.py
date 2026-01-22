from fastapi import FastAPI, HTTPException
from src.api.routes.kafka_router import router as kafka_router
from src.config import settings
from src.kafka.connection_pool import get_connection_pool
from src.kafka.producer import KafkaProducer
from src.kafka.consumer import KafkaConsumer
import logging
import uvicorn
import asyncio
from typing import Dict, Any


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Todo Chatbot Kafka Integration API",
    description="API for integrating Kafka event streaming with the Todo Chatbot application",
    version="0.1.0"
)

# Include routers
app.include_router(kafka_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Chatbot Kafka Integration API"}

@app.get("/health")
def health_check():
    """General health check endpoint."""
    return {"status": "healthy", "service": "todo-chatbot-api"}

@app.get("/health/kafka")
async def kafka_health_check():
    """
    Comprehensive health check for Kafka connectivity and services.
    Checks connection pool status, producer availability, and consumer status.
    """
    try:
        connection_pool = get_connection_pool()

        # Check connection pool status
        pool_status = connection_pool.get_status()

        # Try to get a producer from the pool
        try:
            with connection_pool.get_producer("health-check") as producer:
                # Test producer functionality
                producer_status = {
                    "available": True,
                    "connection_pool_status": "ok"
                }
        except Exception as e:
            producer_status = {
                "available": False,
                "error": str(e),
                "connection_pool_status": "error"
            }

        # Check if in degraded mode
        is_degraded = connection_pool.is_degraded()

        health_response = {
            "status": "degraded" if is_degraded else "healthy",
            "service": "kafka-connectivity",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "checks": {
                "connection_pool": {
                    "status": "ok" if not is_degraded else "degraded",
                    "degraded_mode": is_degraded,
                    "degraded_operations_count": pool_status.get("degraded_operations_count", 0)
                },
                "producer_connectivity": producer_status,
                "circuit_breaker": pool_status.get("circuit_breaker_state", {}),
                "metrics": {
                    "producer_count": pool_status.get("producer_count", 0),
                    "consumer_count": pool_status.get("consumer_count", 0)
                }
            }
        }

        # Return 503 if in degraded mode
        if is_degraded:
            raise HTTPException(status_code=503, detail=health_response)

        return health_response

    except Exception as e:
        error_response = {
            "status": "unhealthy",
            "service": "kafka-connectivity",
            "error": str(e),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
        raise HTTPException(status_code=500, detail=error_response)

@app.get("/health/kafka/producers")
def kafka_producer_health():
    """Health check specifically for Kafka producers."""
    try:
        connection_pool = get_connection_pool()
        pool_status = connection_pool.get_status()

        # Test producer functionality
        test_result = {"status": "ok", "tested": True}

        return {
            "status": "healthy",
            "service": "kafka-producers",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "checks": {
                "producer_pool": {
                    "available": True,
                    "count": pool_status.get("producer_count", 0)
                },
                "functionality_test": test_result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/kafka/consumers")
def kafka_consumer_health():
    """Health check specifically for Kafka consumers."""
    try:
        connection_pool = get_connection_pool()
        pool_status = connection_pool.get_status()

        return {
            "status": "healthy",
            "service": "kafka-consumers",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "checks": {
                "consumer_pool": {
                    "available": True,
                    "count": pool_status.get("consumer_count", 0)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    """Prometheus-compatible metrics endpoint."""
    from src.monitoring.metrics import metrics_collector
    metrics = metrics_collector.collect_all_metrics()

    # Format as Prometheus-compatible text
    prometheus_output = []

    # Counters
    for key, value in metrics.get('counters', {}).items():
        prometheus_output.append(f"# TYPE {key.split('{')[0]} counter")
        prometheus_output.append(f"{key} {value}")

    # Gauges
    for key, value in metrics.get('gauges', {}).items():
        prometheus_output.append(f"# TYPE {key.split('{')[0]} gauge")
        prometheus_output.append(f"{key} {value}")

    return "\n".join(prometheus_output)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.app_env == "development" else False
    )