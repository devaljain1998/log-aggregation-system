from typing import Optional
from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
import os
from routers import health_router

app = FastAPI()

# Global singleton for Elasticsearch client
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
elastic_client = Elasticsearch([ELASTICSEARCH_HOST])
if not elastic_client.ping():
    raise HTTPException(status_code=500, detail="Elasticsearch cluster is not available")

INDEX_NAME = "logs"

@app.on_event("startup")
def startup():
    if not elastic_client.indices.exists(index=INDEX_NAME):
        elastic_client.indices.create(index=INDEX_NAME)

# Include the health and logs routers in the main app
app.include_router(health_router)