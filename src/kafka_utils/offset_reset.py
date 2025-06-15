# src/kafka_utils/offset_reset.py

import logging
from collections import defaultdict
from confluent_kafka import TopicPartition
from confluent_kafka.admin import AdminClient


def list_partitions(admin: AdminClient, topic: str) -> list[TopicPartition]:
    """
    Retrieve all partitions for a given topic.
    """
    metadata = admin.list_topics(topic=topic, timeout=10)
    if topic not in metadata.topics:
        raise ValueError(f"❌ Topic '{topic}' does not exist.")
    return [
        TopicPartition(topic, p.id)
        for p in metadata.topics[topic].partitions.values()
    ]


def reset_offsets(
    group_id: str,
    topic: str,
    bootstrap_servers: str,
    reset_to: str = "earliest",
    partitions: list[int] = None
):
    """
    Reset consumer group offsets to 'earliest' (offset 0) or 'latest' (offset -1)
    for the specified topic and partitions.

    Parameters:
    - group_id: The Kafka consumer group to reset.
    - topic: Kafka topic name.
    - bootstrap_servers: Kafka bootstrap servers.
    - reset_to: 'earliest' or 'latest'.
    - partitions: Optional list of partition integers. If None, all partitions are reset.
    """
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})
    all_partitions = list_partitions(admin, topic)

    if partitions is not None:
        target_partitions = [tp for tp in all_partitions if tp.partition in partitions]
        if not target_partitions:
            raise ValueError(f"❌ No matching partitions found in topic '{topic}'")
    else:
        target_partitions = all_partitions

    target_offset = 0 if reset_to == "earliest" else -1

    # ✅ Correct nested dictionary format required by the Admin API
    offsets_map = defaultdict(dict)
    for tp in target_partitions:
        offsets_map[tp.topic][tp.partition] = target_offset

    logging.info(f"🔁 Setting offsets to '{reset_to}' for group '{group_id}' on topic '{topic}'")

    # ✅ Use keyword arguments (not positional)
    future_map = admin.alter_consumer_group_offsets(
        group_id=group_id,
        offsets=offsets_map
    )

    for topic_name, partition_futures in future_map.items():
        for partition, fut in partition_futures.items():
            try:
                fut.result()
                logging.info(f"✅ Offset set to {target_offset} for {topic_name}[{partition}]")
            except Exception as e:
                logging.warning(f"⚠️ Failed to set offset for {topic_name}[{partition}]: {e}")