# Open-Source Modular Data Platform (OMDP)

This project implements a containerized, end-to-end data engineering ecosystem designed for high-throughput batch processing and scalable infrastructure. 

The primary objective is to build a robust **Medallion Architecture** using modern orchestration and distributed compute, capable of handling diverse data sources (web scraping, API ingestion, and synthetic generators).

## 🛠 Tech Stack
* **Orchestration:** Apache Airflow
* **Compute:** Apache Spark (Multi-node Cluster)
* **Storage:** MinIO (S3-Compatible Object Store)
* **Format:** Parquet / Apache Iceberg (Planned)
* **Environment:** Docker & Docker Compose

## 🏗 System Architecture
The platform is designed to decouple the ingestion, processing, and storage layers, allowing for independent scaling of Spark executors and seamless integration of new data providers.



## 🚀 Roadmap: Phase 1 (Foundation)
The current focus is establishing the core "plumbing" of the system:
1.  **Infrastructure as Code:** Orchestrating a 5-service Docker environment.
2.  **Connectivity Proof:** Validating the S3A protocol between Spark and MinIO.
3.  **End-to-End Pipeline:** Automating a "Synthetic-to-Bronze-to-Silver" data flow.

---