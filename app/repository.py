from typing import Optional
from elasticsearch import Elasticsearch
from app.schemas import LogEntry
from loguru import logger
from app.exceptions import InvalidSearchParameterException

LOGS_INDEX = "logs"


class LogRepository:
    """
    Repository responsible for interacting with the Elasticsearch backend.
    """

    def __init__(self, es_client: Elasticsearch):
        if es_client is None:
            raise ValueError("Elasticsearch client is not initialized")
        self.es_client = es_client

    def save_log(self, log_entry: LogEntry):
        """
        Index a log entry in Elasticsearch.

        Args:
            log (LogEntry): The log entry to index.
        """
        logger.debug(f"save log query: {log_entry.model_dump_json()}")
        r = self.es_client.index(index=LOGS_INDEX, body=log_entry.model_dump())
        return r

    def search_logs(
        self,
        query: Optional[str] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ):
        """
        Search logs in Elasticsearch based on various filters.

        Args:
            query: The search query to filter logs by message content.
            level: The log level to filter logs (e.g., 'INFO', 'ERROR').
            service: The service name to filter logs.
            start_time: The start time to filter logs (ISO 8601 format).
            end_time: The end time to filter logs (ISO 8601 format).

        Returns:
            list: A list of logs matching the filters.
        """
        # if none of the parameters are provided, return exception:
        if not any([query, level, service, start_time, end_time]):
            raise InvalidSearchParameterException()

        search_query = {"query": {"bool": {"must": []}}}
        search_match_query = search_query["query"]["bool"]["must"]
        if query:
            search_match_query.append({"match": {"message": query}})
        if level:
            search_match_query.append({"match": {"level": level}})
        if service:
            search_match_query.append({"match": {"service": service}})
        if start_time and end_time:
            search_query["query"]["bool"]["must"].append(
                {"range": {"timestamp": {"gte": start_time, "lte": end_time}}}
            )

        logger.debug(f"search logs query: {search_query}")

        response = self.es_client.search(index=LOGS_INDEX, body=search_query)
        return response["hits"]["hits"]

    def count_by_field(
        self, service: Optional[str] = None, log_level: Optional[str] = None
    ):
        """
        Aggregate logs in Elasticsearch based on service and/or log level.

        Args:
            service: The service name to filter logs by.
            log_level: The log level to filter logs by.

        Returns:
            dict: A dictionary containing the
                count of logs grouped by the specified field(s).
        """
        if not service and not log_level:
            raise ValueError(
                "At least one filter (service or log_level) must be provided"
            )

        search_query = {
            "size": 0,
            "query": {"bool": {"must": []}},
            "aggs": {"counts": {"composite": {"sources": []}}},
        }

        # Add filters if provided
        search_match_query = search_query["query"]["bool"]["must"]
        search_count_query = search_query["aggs"]["counts"]["composite"][
            "sources"
        ]
        if service:
            search_match_query.append({"term": {"service": service}})
            search_count_query.append(
                {"service": {"terms": {"field": "service"}}}
            )

        if log_level:
            search_match_query.append({"term": {"level": log_level}})
            search_count_query.append(
                {"log_level": {"terms": {"field": "level"}}}
            )

        logger.debug(f"count by field query: {search_query}")
        response = self.es_client.search(index=LOGS_INDEX, body=search_query)
        return response["aggregations"]["counts"]["buckets"]
