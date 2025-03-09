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
def aggregate_logs(
    service: Optional[str] = None,
    log_level: Optional[str] = None,
):
    if not service and not log_level:
        raise ValueError(
            "At least one filter (service or log_level) must be provided"
        )

    return log_query_service.count_by_field(service, log_level)
