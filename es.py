import os
from fastapi import HTTPException
from elasticsearch import Elasticsearch

# Global singleton for Elasticsearch client
ELASTICSEARCH_HOST = os.getenv(
    "ELASTICSEARCH_HOST",
    "http://elasticsearch:9200"
)
elastic_client = Elasticsearch([ELASTICSEARCH_HOST])
if not elastic_client.ping():
    raise HTTPException(
        status_code=500, detail="Elasticsearch cluster is not available"
    )
