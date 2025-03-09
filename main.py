import os
import sys
from fastapi import FastAPI
from loguru import logger
import es
from routers import health_router, logs_router

logger.remove()
logger.add(sys.stdout, level="DEBUG")

app = FastAPI()

INDEX_NAME = "logs"


@app.on_event("startup")
def startup():
    logger.info("In startup event")
    es_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")

    # Ensure Elasticsearch client is created before any operations
    es.get_or_create_elasticsearch_client(es_host)
    es.check_elasticsearch()

    if not es.elastic_client.indices.exists(index=INDEX_NAME):
        logger.info(f"Creating index: {INDEX_NAME}")
        es.create_index(INDEX_NAME)

    logger.info("Application started")


app.include_router(health_router)
app.include_router(logs_router)
