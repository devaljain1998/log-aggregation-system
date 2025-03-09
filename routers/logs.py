from fastapi import APIRouter
from typing import Optional
from app.schemas import LogEntry
from app.services import LogIngestionService, LogQueryService
from app.repository import LogRepository
from es import elastic_client

logs_router = APIRouter(prefix="/logs", tags=["Logs"])

log_repository = LogRepository(elastic_client)
log_ingestion_service = LogIngestionService(log_repository)
log_query_service = LogQueryService(log_repository)


@logs_router.post("/ingest")
def ingest_log(log: LogEntry):
    return log_ingestion_service.ingest_log(log)


@logs_router.get("/search")
def search_logs(
    query: Optional[str] = None,
    level: Optional[str] = None,
    service: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
):
    return log_query_service.query_logs(
        query, level, service, start_time, end_time
    )


@logs_router.get("/aggregate")
def aggregate_logs(field: str):
    agg_query = {"size": 0, "aggs": {"log_count": {"terms": {"field": field}}}}
    return log_query_service.query_logs(agg_query)
