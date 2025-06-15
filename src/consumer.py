#!/usr/bin/env python3

"""
📥 Kafka Order Consumer CLI

Consumes messages from the `orders` Kafka topic, applies business rules,
and persists valid ones to a file. Supports filtering, dry-run mode,
summary stats, and offset resets via Admin API.

Advanced Offset Reset Support:
------------------------------
• Reset offsets for all or specific partitions
• Reset to 'earliest' or 'latest' via --reset-to
• No dependency on kafka-consumer-groups CLI

Usage Examples:
---------------
python src/consumer.py consume
python src/consumer.py consume --dry-run --filter user=alice
python src/consumer.py consume --reset --reset-to latest --partitions 0,2 --summary
python src/consumer.py consume --persist-to myfile.jsonl --group test-group
"""

import argparse
import json
import logging
import signal
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.error import ValueDeserializationError
from confluent_kafka.admin import AdminClient
from service.order_processor import KafkaOrderProcessor
from kafka_utils.offset_reset import reset_offsets
import config

running = True


def signal_handler(sig, frame):
    global running
    logging.info("🛑 Graceful shutdown initiated...")
    running = False


def create_consumer(group_id):
    return DeserializingConsumer({
        "bootstrap.servers": config.BOOTSTRAP_SERVERS,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "key.deserializer": config.get_key_deserializer(),
        "value.deserializer": config.get_value_deserializer(),
    })


def handle_message(msg, processor, dry_run, persist_path, filter_user, stats):
    if msg is None or msg.error():
        return
    stats["total"] += 1

    order = msg.value()
    if filter_user and order.get("user") != filter_user:
        logging.info(f"⏩ Skipped (not user='{filter_user}'): {order}")
        stats["skipped"] += 1
        return

    logging.info(f"📥 Received: {order}")
    if processor.process(order):
        stats["processed"] += 1
        if not dry_run:
            with open(persist_path, "a") as f:
                json.dump(order, f)
                f.write("\n")
    else:
        stats["skipped"] += 1


def consume(group_id, dry_run, do_reset, persist_path, filter_user, show_summary, reset_to, partition_str):
    if do_reset:
        partitions = [int(p.strip()) for p in partition_str.split(",")] if partition_str else None
        reset_offsets(
            group_id=group_id,
            topic=config.TOPIC,
            bootstrap_servers=config.BOOTSTRAP_SERVERS,
            reset_to=reset_to,
            partitions=partitions
        )

    processor = KafkaOrderProcessor()
    consumer = create_consumer(group_id)
    consumer.subscribe([config.TOPIC])

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    stats = {"total": 0, "processed": 0, "skipped": 0}

    while running:
        try:
            msg = consumer.poll(1.0)
        except ValueDeserializationError as e:
            logging.error(f"❌ Deserialization error: {e}, skipping message.")
            continue
        handle_message(msg, processor, dry_run, persist_path, filter_user, stats)

    consumer.close()

    if show_summary:
        print("\n📊 Summary:")
        print(f"• Total messages received:  {stats['total']}")
        print(f"• ✅ Valid orders processed: {stats['processed']}")
        print(f"• ❌ Orders skipped:         {stats['skipped']}")


def main():
    parser = argparse.ArgumentParser(description="Kafka Order Consumer CLI")
    subparsers = parser.add_subparsers(dest="command")

    consume_parser = subparsers.add_parser("consume", help="Start consuming orders")
    consume_parser.add_argument("--group", default=config.GROUP_ID, help="Kafka consumer group ID")
    consume_parser.add_argument("--dry-run", action="store_true", help="Don't write to file")
    consume_parser.add_argument("--reset", action="store_true", help="Reset offsets before consuming")
    consume_parser.add_argument("--reset-to", choices=["earliest", "latest"], default="earliest", help="Offset reset direction")
    consume_parser.add_argument("--partitions", type=str, help="Comma-separated partition list (e.g. 0,2)")
    consume_parser.add_argument("--persist-to", default="storage/orders.jsonl", help="File to persist valid orders")
    consume_parser.add_argument("--filter", type=str, help="Filter by user (e.g. user=alice)")
    consume_parser.add_argument("--summary", action="store_true", help="Show summary report")

    args = parser.parse_args()

    if args.command == "consume":
        filter_user = None
        if args.filter:
            key, val = args.filter.split("=")
            if key != "user":
                raise ValueError("Only '--filter user=<name>' is supported.")
            filter_user = val

        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        consume(
            group_id=args.group,
            dry_run=args.dry_run,
            do_reset=args.reset,
            persist_path=args.persist_to,
            filter_user=filter_user,
            show_summary=args.summary,
            reset_to=args.reset_to,
            partition_str=args.partitions,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()