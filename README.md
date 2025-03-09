# Log Aggregation System

## 🚀 Overview
The **Log Aggregation System** is a centralized solution for collecting, processing, and storing logs from multiple sources. It provides a streamlined platform for monitoring, analyzing, and troubleshooting system logs to enhance performance and reliability.

## 📌 Features
- 🔍 **Centralized Log Collection** – Aggregate logs from various services in one place.
- 📊 **Search & Query** – Quickly filter and analyze logs based on multiple criteria.
- ⚡ **Fast Ingestion** – Efficiently process and store logs using Elasticsearch.
- 🔥 **Real-time Monitoring** – Get insights into your system's behavior instantly.
- 🔄 **Hot-Reload Support** – Automatically updates when changes are made during development.

---

## 🛠 Installation & Setup

### 🔹 Prerequisites
Ensure you have the following installed before setting up:
- **Docker & Docker Compose** ([Install Guide](https://docs.docker.com/get-docker/))
- **Python 3.8+** ([Install Guide](https://www.python.org/downloads/))

### 🔹 Installation Steps
1. **Clone the repository:**
2. **Build and start services using Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will start the necessary services including Elasticsearch and the API server.

---

## 🔍 Usage

### ▶️ Running the System
To start the Log Aggregation System manually:
Just need to start using `docker-compose up --build` and the elastic-search DB and the backend server starts!

### 🔥 Hot-Reload (for Development)
The system supports hot-reloading to automatically reflect code changes:
```bash
uvicorn main:app --reload
```

---

## ✅ Setting Up Pre-Commit Hooks
To enforce coding standards, set up pre-commit hooks with:
```bash
pip install -r requirements.txt
pre-commit install
```
This will automatically format and lint code before committing changes.

---

## 🧪 Running Tests
Run the test suite with:
```bash
pytest
```
Ensure test dependencies are installed:
```bash
pip install -r requirements-test.txt
```
This project uses [Testcontainers](https://testcontainers-python.readthedocs.io/en/latest/) to provide a reliable test environment with Docker.

---

## API Documentation
Once the system is running, you can explore the API documentation at:
- Swagger UI: http://localhost:8000/docs



## 📬 API Testing with Postman
A Postman collection is available for testing API endpoints:
1. Import `Log Aggregation System.postman_collection.json` into Postman.
2. Use the predefined requests to interact with the system.

---

## 🤝 Contributing
We welcome contributions! To contribute:
1. **Fork the repository** on GitHub.
2. **Create a new branch** for your feature.
3. **Submit a Pull Request (PR)** with a detailed description.

Happy coding! 🚀
