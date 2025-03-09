from typing import Optional
from app.repository import LogRepository
from app.schemas import LogEntry


class LogIngestionService:
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    def ingest_log(self, log_entry: LogEntry):
        return self.log_repository.save_log(log_entry)


class LogQueryService:
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    def query_logs(
        self,
        query: Optional[str] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ):
        return self.log_repository.search_logs(
            query, level, service, start_time, end_time
        )
