from typing import Optional
from app.repository import LogRepository
from app.schemas import LogEntry


class LogIngestionService:
    """
    Service responsible for ingesting logs into the system.
    """

    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    def ingest_log(self, log_entry: LogEntry):
        """
        Ingest a log entry into the system.

        Args:
            log (LogEntry): The log entry to ingest.
        """
        return self.log_repository.save_log(log_entry)


class LogQueryService:
    """
    Service responsible for querying logs from the system.
    """

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
        """
        Query logs based on various filters.

        Args:
            query: The search query to filter logs by message content.
            level: The log level to filter logs (e.g., 'INFO', 'ERROR').
            service: The service name to filter logs.
            start_time: The start time to filter logs (ISO 8601 format).
            end_time: The end time to filter logs (ISO 8601 format).

        Returns:
            list: A list of logs matching the filters.
        """
        return self.log_repository.search_logs(
            query, level, service, start_time, end_time
        )

    def count_by_field(
        self, service: Optional[str] = None, log_level: Optional[str] = None
    ):
        """
        Aggregate logs based on service and/or log level.

        Args:
            service: The service name to filter logs by.
            log_level: The log level to filter logs by.

        Returns:
            dict: A dictionary containing the count of logs
                grouped by the specified field(s).
        """
        return self.log_repository.count_by_field(service, log_level)
