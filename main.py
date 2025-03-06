from typing import Optional
from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os

app = FastAPI()

# Connect to Elasticsearch
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
elastic_client = Elasticsearch([ELASTICSEARCH_HOST])
if not elastic_client.ping():
    raise HTTPException(status_code=500, detail="Elasticsearch cluster is not available")