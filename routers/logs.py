from fastapi import APIRouter, Depends
from typing import Optional
from app.schemas import LogEntry
from app.services import LogIngestionService, LogQueryService
from app.repository import LogRepository
from es import get_or_create_elasticsearch_client

logs_router = APIRouter(prefix="/logs", tags=["Logs"])


def get_log_repository() -> LogRepository:
    elastic_client = get_or_create_elasticsearch_client()
    return LogRepository(elastic_client)


def get_log_ingestion_service(
    log_repository: LogRepository = Depends(get_log_repository),  # noqa: B008
) -> LogIngestionService:
    return LogIngestionService(log_repository)


def get_log_query_service(
    log_repository: LogRepository = Depends(get_log_repository),  # noqa: B008
) -> LogQueryService:
    return LogQueryService(log_repository)


@logs_router.post("/ingest")
def ingest_log(
    log: LogEntry,
    log_ingestion_service: LogIngestionService = Depends(  # noqa: B008
        get_log_ingestion_service
    ),
):
    """
    Ingest a log entry into the system.
    """
    return log_ingestion_service.ingest_log(log)


@logs_router.get("/search")
def search_logs(
    query: Optional[str] = None,
    level: Optional[str] = None,
    service: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    log_query_service: LogQueryService = Depends(  # noqa: B008
        get_log_query_service
    ),  # noqa: B008
):
    """
    Search logs based on various filters.
    """

    return log_query_service.query_logs(
        query, level, service, start_time, end_time
    )


@logs_router.get("/aggregate")
def aggregate_logs(
    service: Optional[str] = None,
    log_level: Optional[str] = None,
    log_query_service: LogQueryService = Depends(  # noqa: B008
        get_log_query_service
    ),
):
    """
    Endpoint to aggregate logs based on service and/or log level.

    Raises:
        ValueError: If neither service nor log_level is provided.
    """

    if not service and not log_level:
        raise ValueError(
            "At least one filter (service or log_level) must be provided"
        )

    return log_query_service.count_by_field(service, log_level)
