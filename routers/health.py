from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch
import os

# Create a router for health check APIs
health_router = APIRouter()

# Health check API for FastAPI server
@health_router.get("/health")
def health_check():
    return {"status": "ok"}

# Health check API for Elasticsearch
# @health_router.get("/health/elasticsearch")
# def elasticsearch_health_check():
#     if elastic_client.ping():
#         return {"status": "ok"}
#     else:
#         raise HTTPException(status_code=500, detail="Elasticsearch cluster is not available")
