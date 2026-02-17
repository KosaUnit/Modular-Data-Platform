# Telecom Network Event Pipeline (Local Lakehouse + Kafka + Spark + Airflow + MinIO + Grafana)

A dockerized, local-first data engineering project that simulates telecom network events and processes them through Kafka and Spark into lakehouse-style storage layers (Bronze/Gold) on S3-compatible object storage (MinIO). Airflow orchestrates ingestion and aggregation jobs. Grafana visualizes operational and business KPIs.

This project is designed for hands-on practice with:
- Docker / Docker Compose
- Kafka (topics, partitions, consumer groups)
- Spark (Kafka source, Structured Streaming or micro-batch reads, Parquet partitioning)
- Lakehouse layers (Bronze → Gold)
- Airflow orchestration
- MinIO (local S3-compatible storage), later AWS S3
- Grafana dashboards
- CI/CD foundations and (later) monitoring

## System overview

### Data flow (local)
1. **Event Generator (Python)** emits realistic telecom events (4 event types) and produces them to Kafka.
2. **Kafka** buffers events in a small number of topics/partitions to keep local resources low.
3. **Spark Job #1 (Bronze Ingestion)** runs on a schedule via Airflow, reads from Kafka, writes raw canonical events to **Bronze** in MinIO.
4. **Spark Job #2 (Gold Aggregation)** runs less often via Airflow, reads Bronze, produces aggregated KPI tables to **Gold** (optionally also writes to Postgres for Grafana).
5. **Grafana** visualizes KPIs and pipeline health.

### Logical reasoning for scheduling
- Bronze ingestion is run as a micro-batch job every **1–5 minutes** to balance “near real-time” visibility with local resource constraints.
- Gold aggregation runs every **15 minutes or hourly**, since aggregates can lag slightly without harming operational insight.

## Tech stack
- Python (event generator, utilities)
- Kafka (KRaft-based single broker for local dev)
- Spark (Structured Streaming / batch)
- Airflow (DAG orchestration)
- MinIO (Bronze/Gold storage; later migration to AWS S3)
- Grafana (dashboards)
- (Optional) Postgres (serving layer for Grafana)
- GitHub Actions (CI/CD)
- (Later) Prometheus + exporters (monitoring)

## Repository layout (proposed)
- `infra/`
  - `docker-compose.yml`
  - `kafka/` (broker config)
  - `minio/` (buckets init)
  - `airflow/` (DAGs, Dockerfile)
  - `spark/` (Spark image/config)
  - `grafana/` (datasources, dashboards)
- `services/`
  - `event-generator/`
  - `spark-bronze/`
  - `spark-gold/`
- `docs/`
  - `events_wiki.md`
  - `data_wiki.md`
  - `project_plan.md`

## Event types (high level)
See `docs/events_wiki.md`.
- `call_detail` (voice call attempt/completion/drop)
- `data_session` (mobile data session latency/throughput/errors)
- `handover` (cell tower handover success/failure)
- `tower_health` (tower load/availability/alarms)

## Data layers
See `docs/data_wiki.md`.
- **Bronze:** immutable-ish, raw canonical events written as partitioned parquet
- **Gold:** curated aggregates/KPIs for dashboards and analysis

## Roadmap
See `docs/project_plan.md`. Quick view:
- Phase 1: Docker infra + generator + Kafka topics
- Phase 2: Airflow + Spark Bronze ingestion to MinIO
- Phase 3: Spark Gold aggregation
- Phase 4: Grafana dashboards
- Phase 5: CI/CD baseline
- Phase 6: Monitoring/observability
- Phase 7: MinIO → S3 migration
