import time
from fastapi.testclient import TestClient
import es
from main import app
from elasticsearch import Elasticsearch
from testcontainers.elasticsearch import ElasticSearchContainer
import pytest

client = TestClient(app)


@pytest.fixture(scope="module")
def elasticsearch_container():
    """
    Fixture to start an Elasticsearch container for testing.
    """
    with ElasticSearchContainer(
        "docker.elastic.co/elasticsearch/elasticsearch:7.17.9"
    ) as container:
        time.sleep(10)  # Wait for Elasticsearch to be ready
        yield container


@pytest.fixture(scope="module")
def elasticsearch_client(elasticsearch_container):
    """
    Fixture to create an Elasticsearch client and set up the 'logs' index.
    """
    client = Elasticsearch([elasticsearch_container.get_url()])
    es.get_or_create_elasticsearch_client(elasticsearch_container.get_url())
    es.create_index("logs")
    yield client
    client.indices.delete(index="logs")  # Cleanup


@pytest.fixture(scope="module", autouse=True)
def setup_elasticsearch_data(elasticsearch_client):
    """
    Fixture to set up initial log data in Elasticsearch for testing.
    """
    log_entries = [
        {
            "timestamp": "2024-01-29T10:00:00Z",
            "level": "ERROR",
            "service": "test-svc",
            "message": "Connection timeout",
        },
        {
            "timestamp": "2024-01-30T10:00:00Z",
            "level": "ERROR",
            "service": "test-svc",
            "message": "Connection timeout",
        },
        {
            "timestamp": "2024-01-31T10:00:00Z",
            "level": "ERROR",
            "service": "test-svc",
            "message": "Connection timeout",
        },
    ]
    for log_entry in log_entries:
        elasticsearch_client.index(index="logs", body=log_entry)

    elasticsearch_client.indices.refresh(
        index="logs"
    )  # Ensure data is available

    yield  # Allow tests to run

    # Cleanup after tests
    query = {"query": {"match": {"service": "test-svc"}}}
    elasticsearch_client.delete_by_query(index="logs", body=query)


def test_ingest_log():
    """
    Test the log ingestion endpoint.
    """
    log_entry = {
        "timestamp": "2024-02-01T10:00:00Z",
        "level": "ERROR",
        "service": "test-svc",
        "message": "Connection timeout",
    }
    response = client.post("/logs/ingest", json=log_entry)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["result"] == "created"
    assert response_data["_shards"]["successful"] == 1


def test_search_logs():
    """
    Test the log search endpoint.
    """
    response = client.get("/logs/search", params={"service": "test-svc"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
    for log in response_data:
        assert log["_source"]["service"] == "test-svc"
        assert log["_source"]["level"] == "ERROR"
        assert log["_source"]["message"] == "Connection timeout"


def test_search_logs_within_time_range():
    """
    Test the log search endpoint with start_time and end_time parameters.
    """
    start_time = "2024-01-29T00:00:00Z"
    end_time = "2024-01-30T23:59:59Z"
    response = client.get(
        "/logs/search",
        params={
            "service": "test-svc",
            "start_time": start_time,
            "end_time": end_time,
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert (
        len(response_data) == 2
    )  # Only two logs within the specified time range
    for log in response_data:
        assert log["_source"]["service"] == "test-svc"
        assert log["_source"]["level"] == "ERROR"
        assert log["_source"]["message"] == "Connection timeout"
        assert start_time <= log["_source"]["timestamp"] <= end_time


def test_search_logs_outside_time_range():
    """
    Test the log search endpoint with start_time and
    end_time parameters outside the log range.
    """
    start_time = "2024-02-01T00:00:00Z"
    end_time = "2024-02-02T23:59:59Z"
    response = client.get(
        "/logs/search",
        params={
            "service": "test-svc",
            "start_time": start_time,
            "end_time": end_time,
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0  # No logs within the specified time range


def test_aggregate_logs_service():
    """
    Test the log aggregation by service endpoint.
    """
    response = client.get("/logs/aggregate", params={"service": "test-svc"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["key"]["service"] == "test-svc"
    assert response_data[0]["doc_count"] == 3


def test_aggregate_logs_log_level_present():
    """
    Test the log aggregation by log level endpoint when logs are present.
    """
    response = client.get("/logs/aggregate", params={"log_level": "ERROR"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["key"]["log_level"].lower() == "error"
    assert response_data[0]["doc_count"] == 3


def test_aggregate_logs_log_level_not_present():
    """
    Test the log aggregation by log level endpoint when no logs are present.
    """
    response = client.get("/logs/aggregate", params={"log_level": "INFO"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0  # No logs with INFO level
