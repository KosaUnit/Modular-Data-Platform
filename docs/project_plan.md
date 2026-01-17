Phase 1: Core Infrastructure & Baseline Pipeline
Goal: Establish a stable, multi-container environment where Airflow, Spark, and MinIO interact seamlessly using the S3A protocol.

1.1 Environment & Service Orchestration
[x] Docker Network Layer: Define a dedicated bridge network for service discovery (e.g., data-platform-network).

[x] MinIO (Storage Layer): - [ ] Deploy MinIO container with Console enabled.

[x] Initialize bronze (raw) and silver (processed) buckets.

[x] Configure access keys and secret keys via .env.

<!-- Postpone Spark - I don't need it know - use something instead. -->

<!-- [ ] Apache Spark (Compute Layer): -->

<!-- [ ] Deploy Spark Master node. -->

<!-- [ ] Deploy 1x Spark Worker node (scalable to multi-node). -->

<!-- [ ] Provision jars/ volume to handle S3A and AWS SDK dependencies. -->

[ ] Apache Airflow (Orchestration Layer):

[ ] Deploy Airflow Webserver, Scheduler, and Postgres backend.

[ ] Map local volumes for /dags, /logs, and /scripts.

1.2 The Ingestion Pipeline (Producer)
[ ] Ingestion Script: Develop a Python-based "Pulse" generator using boto3.

[x] Requirement: Programmatically detect/create buckets.

[x] Requirement: Upload timestamped JSON payloads to s3a://bronze/.

[x] Dockerization: Create a standalone Dockerfile for the Ingestion service to run as a transient task.

1.3 The Processing Layer (Spark Job)
[x] Spark-to-S3 Connectivity: - [ ] Implement SparkSession configuration for S3A endpoint (pointing to MinIO container).

<!-- [ ] Validate JAR compatibility (hadoop-aws and aws-java-sdk-bundle). -->

[ ] ETL Logic: - [ ] Read raw JSON from bronze.

[ ] Enforce schema and apply "Processed At" metadata columns.

[ ] Write optimized Parquet output to s3a://silver/.

1.4 Orchestration & Automation (DAG)
[ ] Airflow Connections: Define spark_default and aws_default (MinIO) connections in the Airflow UI.

[ ] DAG Design:

[ ] Task 1: Run Ingestion Container.

[ ] Task 2: S3KeySensor to verify data arrival in bronze.

[ ] Task 3: SparkSubmitOperator to trigger processing job.

[ ] End-to-End Validation: Execute full DAG and verify Parquet file existence in MinIO.

Phase 2: System Hardening & Real-World Ingestion
Note: Details to be refined after Phase 1 completion.

[ ] Medallion Architecture: Implement a gold layer for aggregated/analytical views.

[ ] Real-World Scraper: Replace synthetic "Pulse" generator with a modular web-scraping service (BeautifulSoup/Selenium).

[ ] Schema Evolution: Integrate Apache Iceberg or Delta Lake for ACID transactions on S3.

Phase 3: Observability & Serving
[ ] Data Quality: Integrate Great Expectations as a validation step between Bronze and Silver layers.

[ ] Visualization Layer: Connect a BI tool (Metabase/Superset) or a Streamlit app to the silver/gold Parquet files.

[ ] Monitoring: Implement Airflow Callback alerts for pipeline failures.
