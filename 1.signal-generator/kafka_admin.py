from confluent_kafka.admin import AdminClient, NewTopic

def create_topic(
    bootstrap_servers: str,
    topic_name: str,
    num_partitions: int,
    replication_factor: int,
    config: dict = None,
) -> None:
    """
    Explicitly create a Kafka topic with full control over its configuration.
    """

    # AdminClient is Kafka's management interface.
    # It lets you create/delete topics, inspect cluster state, etc.
    # It does NOT produce or consume messages - it's purely for administration.
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})

    # Per-topic configuration overrides.
    # These are applied on top of broker defaults and give you precise control.
    topic_config = {
        "retention.ms": "604800000",    # Keep messages for 7 days, then delete them
        "min.insync.replicas": "2",     # A write is only "successful" if 2 replicas confirm it
        "cleanup.policy": "delete",     # Delete old segments when retention limit is hit
    }

    # NewTopic describes the topic you want to create.
    # It does NOT create it yet - it's just a definition object.
    new_topic = NewTopic(
        topic=topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor,
        config=topic_config,
    )

    # create_topics() is async - it returns a dict of {topic_name: Future}.
    # You must call future.result() to actually wait for the operation to complete
    # and to catch any errors (e.g., topic already exists, not enough brokers, etc.)
    futures = admin.create_topics([new_topic])

    for topic, future in futures.items():
        try:
            future.result()
            print(f"✓ Topic '{topic}' created successfully.")
        except Exception as e:
            print(f"X Failed to create topic '{topic}': {e}")

# --- Usage ---
create_topic(
    bootstrap_servers="localhost:9092",
    topic_name="payments.orders.created.prod",
    num_partitions=6,          # 6 consumers can work in parallel at most
    replication_factor=3,      # Survives 1 broker failure without data loss
)