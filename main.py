import sys
from fastapi import FastAPI
from loguru import logger
from routers import health_router, logs_router
from es import create_index, elastic_client

logger.remove()
logger.add(sys.stdout, level="DEBUG")

app = FastAPI()

INDEX_NAME = "logs"


@app.on_event("startup")
def startup():
    if elastic_client.indices.exists(index=INDEX_NAME):
        elastic_client.indices.delete(index=INDEX_NAME)
        logger.info("Existing Elasticsearch index deleted")

    create_index(INDEX_NAME)

    logger.info("Application started")


# Include the health and logs routers in the main app
app.include_router(health_router)
app.include_router(logs_router)
