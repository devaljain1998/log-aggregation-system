from typing import Optional
from elasticsearch import Elasticsearch
from app.schemas import LogEntry
from loguru import logger
from app.exceptions import InvalidSearchParameterException

LOGS_INDEX = "logs"

class LogRepository:
    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client

    def save_log(self, log_entry: LogEntry):
        logger.debug(f"save log query: {log_entry.model_dump_json()}")
        
        response = self.es_client.index(
            index=LOGS_INDEX,
            body=log_entry.model_dump()
        )
        return response

    def search_logs(self, query: Optional[str] = None, level: Optional[str] = None, service: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None):
        # if none of the parameters are provided, return exception:
        if not any([query, level, service, start_time, end_time]):
            raise InvalidSearchParameterException()
        
        search_query = {"query": {"bool": {"must": []}}}                
        if query:
            search_query["query"]["bool"]["must"].append({"match": {"message": query}})
        if level:
            search_query["query"]["bool"]["must"].append({"match": {"level": level}})
        if service:
            search_query["query"]["bool"]["must"].append({"match": {"service": service}})
        if start_time and end_time:
            search_query["query"]["bool"]["must"].append({"range": {"timestamp": {"gte": start_time, "lte": end_time}}})        
        
        logger.debug(f"search logs query: {search_query}")
        
        response = self.es_client.search(
            index=LOGS_INDEX,
            body=search_query
        )
        return response['hits']['hits']
