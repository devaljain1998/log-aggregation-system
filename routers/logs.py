from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import Optional
from es import elastic_client

logs_router = APIRouter()

INDEX_NAME = "logs"

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    service: str

@logs_router.post("/logs/")
def ingest_log(log: LogEntry):
    res = elastic_client.index(index=INDEX_NAME, body=log.model_dump())
    return res["result"]

@logs_router.get("/search/")
def search_logs(query: Optional[str] = None, level: Optional[str] = None, service: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None):
    search_query = {"query": {"bool": {"must": []}}}
    
    if query:
        search_query["query"]["bool"]["must"].append({"match": {"message": query}})
    if level:
        search_query["query"]["bool"]["must"].append({"match": {"level": level}})
    if service:
        search_query["query"]["bool"]["must"].append({"match": {"service": service}})
    if start_time and end_time:
        search_query["query"]["bool"]["must"].append({"range": {"timestamp": {"gte": start_time, "lte": end_time}}})
    
    res = elastic_client.search(index=INDEX_NAME, body=search_query)
    return res["hits"]["hits"]

@logs_router.get("/aggregate/")
def aggregate_logs(field: str):
    agg_query = {
        "size": 0,
        "aggs": {
            "log_count": {
                "terms": {"field": field}
            }
        }
    }
    res = elastic_client.search(index=INDEX_NAME, body=agg_query)
    return res["aggregations"]["log_count"]["buckets"]
