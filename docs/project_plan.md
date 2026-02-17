# Project Plan — Telecom Network Event Pipeline

Phase 1: Core Infrastructure & Local Streaming Baseline  
Goal: Establish a stable, fully dockerized environment where Kafka, Airflow, Spark, and MinIO interact reliably and can process simulated telecom events end-to-end into the Bronze layer.

1.1 Environment & Service Orchestration

[x] Docker Network Layer  
- Dedicated bridge network for service discovery (e.g., telecom-data-platform).

[x] MinIO (Storage Layer)  
- [x] Deploy MinIO container with Console enabled.  
- [x] Initialize bronze and gold buckets.  
- [x] Configure access keys and secret keys via `.env`.

[x] Reuse Existing Development Base  
- [x] Reuse preconfigured MinIO access patterns.  
- [x] Reuse existing S3A connectivity configuration approach.  
- [x] Reuse container structure and environment variable conventions.

[ ] Kafka (Streaming Layer)  
- [ ] Deploy single-node Kafka (KRaft mode, no ZooKeeper).  
- [ ] Define telecom.events topic with low partition count (e.g., 3).  
- [ ] Configure internal and external listeners for Docker network.

[ ] Apache Airflow (Orchestration Layer)  
- [ ] Deploy Airflow Webserver, Scheduler, and Postgres backend.  
- [ ] Map local volumes for `/dags`, `/logs`, `/plugins`, `/scripts`.  
- [ ] Configure Airflow executor (LocalExecutor recommended for start).

[ ] Apache Spark (Compute Layer)  
- [ ] Deploy Spark container (single-node for local development).  
- [ ] Provision JARs for:
  - Kafka connector  
  - Hadoop AWS (S3A)  
- [ ] Externalize Spark configuration via environment variables.

---

1.2 Event Ingestion (Telecom Event Generator → Kafka)

[ ] Event Generator Service (Python)  
- [ ] Implement 4 telecom event types:
  - call_detail  
  - data_session  
  - handover  
  - tower_health  
- [ ] Configurable event rate (events/sec).  
- [ ] Incident simulation mode (tower or region degradation).  
- [ ] Deterministic randomness via seed (for reproducibility).

[ ] Kafka Producer Logic  
- [ ] JSON schema enforcement.  
- [ ] Event key strategy (e.g., tower_id for partitioning).  
- [ ] Delivery confirmation handling.

[ ] Dockerization  
- [ ] Standalone Dockerfile for generator service.  
- [ ] Runtime configuration via environment variables.

[ ] Validation  
- [ ] Produce events and verify consumption via Kafka CLI or Kafka UI.  
- [ ] Confirm realistic event distribution and incident spikes.

---

1.3 Bronze Ingestion — Spark Job #1 (Kafka → MinIO)

[x] Spark-to-S3A Connectivity (Reused Pattern)  
- [x] Implement SparkSession S3A configuration for MinIO endpoint.  
- [x] Validate credential resolution via environment variables.

[ ] Kafka Read Logic  
- [ ] Read from telecom.events topic.  
- [ ] Parse JSON and enforce schema.  
- [ ] Add ingestion metadata columns:
  - ingest_time  
  - batch_id or processing_time

[ ] Bronze Write Logic  
- [ ] Write Parquet to `s3a://bronze/events/`.  
- [ ] Partition by:
  - event_date  
  - event_type  
- [ ] Implement idempotency strategy:
  - offset tracking OR event_id deduplication.

[ ] Orchestration via Airflow DAG  
- [ ] Define Airflow connections:
  - spark_default  
  - aws_default (MinIO)  
- [ ] DAG task: SparkSubmitOperator for Bronze ingestion.  
- [ ] Schedule interval:
  - 1–5 minutes (configurable).

[ ] End-to-End Validation  
- [ ] Execute DAG.  
- [ ] Verify new Parquet files in Bronze.  
- [ ] Confirm no duplicate ingestion on rerun.

---

Phase 2: Gold Aggregation Layer & Serving Readiness  
Goal: Transform Bronze data into aggregated KPI datasets and make them queryable for dashboards.

2.1 Gold Layer — Spark Job #2

[ ] Aggregation Logic  
- [ ] Compute windowed KPIs:
  - call drop rate  
  - call failure rate  
  - handover failure rate  
  - average & p95 latency  
  - active connection averages  
- [ ] Aggregation levels:
  - tower (15 min window)  
  - region (hourly)

[ ] Gold Storage  
- [ ] Write Parquet to `s3a://gold/kpis/`.  
- [ ] Partition by date/hour.

[ ] Orchestration  
- [ ] Airflow DAG task for Gold job.  
- [ ] Schedule interval:
  - every 15 minutes OR hourly.

[ ] Validation  
- [ ] Confirm Gold datasets update incrementally.  
- [ ] Validate metric correctness against Bronze samples.

---

2.2 Serving Layer for Grafana

[ ] Postgres Serving Database (Recommended First Step)  
- [ ] Deploy Postgres container.  
- [ ] Gold job writes aggregated tables to Postgres.  
- [ ] Define upsert strategy.

[ ] Grafana  
- [ ] Deploy Grafana container.  
- [ ] Provision Postgres datasource.  
- [ ] Create dashboards:
  - Network health overview  
  - Top failing towers  
  - Failure/drop rate over time  
  - Pipeline ingestion lag (basic)

---

Phase 3: CI/CD & System Hardening  
Goal: Ensure reproducibility, code quality, and automated validation.

3.1 CI/CD (GitHub Actions)

[ ] Linting & Formatting  
- [ ] ruff  
- [ ] black

[ ] Testing  
- [ ] Unit tests for event generator.  
- [ ] Schema validation tests.

[ ] Docker Build Pipeline  
- [ ] Build all service images.  
- [ ] Compose smoke test:
  - Start Kafka  
  - Run generator briefly  
  - Validate topic contains messages.

[ ] PR Quality Gates  
- [ ] Block merge on failed checks.

---

3.2 Data Reliability

[ ] Dead Letter Strategy  
- [ ] Route malformed events to DLQ topic or storage path.

[ ] Data Quality Checks (later integration point)  
- [ ] Validate required fields in Bronze.  
- [ ] Basic completeness checks per batch.

---

Phase 4: Observability & Monitoring  
Goal: Gain operational visibility into pipeline and infrastructure health.

[ ] Structured Logging  
- [ ] JSON logs for all services.

[ ] Prometheus Stack  
- [ ] Deploy Prometheus.  
- [ ] Kafka exporter.  
- [ ] JVM/Spark metrics.  
- [ ] Airflow metrics.

[ ] Grafana Infrastructure Dashboards  
- [ ] Kafka lag  
- [ ] Spark job duration  
- [ ] Airflow DAG status  
- [ ] MinIO storage usage

[ ] Alerting  
- [ ] Airflow task failure callbacks.  
- [ ] Lag threshold alerts.

---

Phase 5: Cloud Migration Path (MinIO → AWS S3)

Goal: Make storage backend swappable without code changes.

[ ] Externalize storage configuration.  
[ ] Parameterize bucket names and endpoints.  
[ ] Validate Spark jobs against AWS S3.  
[ ] Optional: deploy pipeline on EC2.

