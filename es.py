import os
from fastapi import HTTPException
from elasticsearch import Elasticsearch

from loguru import logger

# Global singleton for Elasticsearch client
ELASTICSEARCH_HOST = os.getenv(
    "ELASTICSEARCH_HOST", "http://elasticsearch:9200"
)
elastic_client = Elasticsearch([ELASTICSEARCH_HOST])


def check_elasticsearch():
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
