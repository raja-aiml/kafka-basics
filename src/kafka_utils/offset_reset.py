# src/kafka_utils/offset_reset.py

import logging
from confluent_kafka import TopicPartition, Consumer
from confluent_kafka.admin import AdminClient


def list_partitions(admin: AdminClient, topic: str) -> list[TopicPartition]:
    """
    Retrieve all partitions for a given topic.
    """
    metadata = admin.list_topics(topic=topic, timeout=10)
    if topic not in metadata.topics:
        raise ValueError(f"❌ Topic '{topic}' does not exist.")
    return [
        TopicPartition(topic, p.id) for p in metadata.topics[topic].partitions.values()
    ]


def reset_offsets(
    group_id: str,
    topic: str,
    bootstrap_servers: str,
    reset_to: str = "earliest",
    partitions: list[int] = None,
):
    """
    Reset consumer group offsets to 'earliest' or 'latest' by committing specified offsets
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

    # Reset offsets by committing specific offsets via a temporary consumer
    consumer_conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "enable.auto.commit": False,
    }
    consumer = Consumer(consumer_conf)
    offsets_to_commit = []
    for tp in target_partitions:
        low, high = consumer.get_watermark_offsets(
            TopicPartition(tp.topic, tp.partition), timeout=10
        )
        desired_offset = low if reset_to == "earliest" else high
        logging.info(
            f"🔁 Partition {tp.partition}: resetting offset to {desired_offset}"
        )
        offsets_to_commit.append(TopicPartition(tp.topic, tp.partition, desired_offset))
    try:
        consumer.commit(offsets=offsets_to_commit, asynchronous=False)
        logging.info(
            f"✅ Offsets for group '{group_id}' on topic '{topic}' successfully reset"
        )
    except Exception as e:
        logging.warning(f"⚠️ Failed to commit offsets: {e}")
    finally:
        consumer.close()
