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
    with ElasticSearchContainer(
        "docker.elastic.co/elasticsearch/elasticsearch:7.17.9"
    ) as container:
        time.sleep(10)  # Wait for Elasticsearch to be ready
        yield container


@pytest.fixture(scope="module")
def elasticsearch_client(elasticsearch_container):
    client = Elasticsearch([elasticsearch_container.get_url()])
    es.get_or_create_elasticsearch_client(elasticsearch_container.get_url())
    es.create_index("logs")
    yield client
    client.indices.delete(index="logs")  # Cleanup


@pytest.fixture(scope="module", autouse=True)
def setup_elasticsearch_data(elasticsearch_client):
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
    response = client.get("/logs/search", params={"service": "test-svc"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
    for log in response_data:
        assert log["_source"]["service"] == "test-svc"
        assert log["_source"]["level"] == "ERROR"
        assert log["_source"]["message"] == "Connection timeout"


def test_aggregate_logs_service():
    response = client.get("/logs/aggregate", params={"service": "test-svc"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["key"]["service"] == "test-svc"
    assert response_data[0]["doc_count"] == 3


def test_aggregate_logs_log_level_present():
    response = client.get("/logs/aggregate", params={"log_level": "ERROR"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["key"]["log_level"].lower() == "error"
    assert response_data[0]["doc_count"] == 3


def test_aggregate_logs_log_level_not_present():
    response = client.get("/logs/aggregate", params={"log_level": "INFO"})
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0  # No logs with INFO level
