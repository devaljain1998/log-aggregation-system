import os
from fastapi import HTTPException
from elasticsearch import Elasticsearch
from loguru import logger

ELASTICSEARCH_HOST = os.getenv(
    "ELASTICSEARCH_HOST", "http://elasticsearch:9200"
)

# Initialize `elastic_client` as None
elastic_client: Elasticsearch = None


def get_or_create_elasticsearch_client(
    host: str = ELASTICSEARCH_HOST,
) -> Elasticsearch:
    global elastic_client
    if elastic_client is None:
        logger.info(f"Connecting to Elasticsearch at {host}")
        elastic_client = Elasticsearch([host])
        logger.info(f"Connected to Elasticsearch at {host}")
    return elastic_client


def check_elasticsearch():
    if elastic_client is None:
        raise HTTPException(
            status_code=500, detail="Elasticsearch client is not initialized"
        )
    if not elastic_client.ping():
        raise HTTPException(
            status_code=500, detail="Elasticsearch cluster is not available"
        )
    logger.info("Elasticsearch cluster is available")


def create_index(index: str):
    index_body = {
        "settings": {
            "index": {"number_of_shards": 1, "number_of_replicas": 1},
            "analysis": {
                "normalizer": {
                    "lowercase_normalizer": {
                        "type": "custom",
                        "char_filter": [],
                        "filter": ["lowercase"],
                    }
                },
                "analyzer": {"default": {"type": "standard"}},
            },
        },
        "mappings": {
            "properties": {
                "timestamp": {"type": "date", "format": "strict_date_time"},
                "level": {
                    "type": "keyword",
                    "normalizer": "lowercase_normalizer",
                    "ignore_above": 256,
                },
                "message": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 512}
                    },
                    "doc_values": False,
                },
                "service": {
                    "type": "keyword",
                    "normalizer": "lowercase_normalizer",
                    "ignore_above": 256,
                },
            }
        },
    }

    elastic_client.indices.create(index=index, body=index_body)
    logger.info(f"Elasticsearch index `{index}` created with proper structure")
