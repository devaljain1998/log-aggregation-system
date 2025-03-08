from fastapi import APIRouter, HTTPException
from es import elastic_client

# Create a router for health check APIs
health_router = APIRouter(prefix="/health", tags=["Health"])


# Health check API for FastAPI server
@health_router.get("/")
def health_check():
    return {"status": "ok"}


# Health check API for Elasticsearch
@health_router.get("/elasticsearch")
def elasticsearch_health_check():
    if elastic_client.ping():
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=500, detail="Elasticsearch cluster is not available"
        )
