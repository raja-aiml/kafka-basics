#!/usr/bin/env python3

"""
🔁 Kafka Order Replayer

Purpose:
--------
Replay previously processed orders from `storage/orders.jsonl` back into
the Kafka `orders` topic for recovery, reprocessing, or testing.

When to use:
------------
- ✅ Re-test consumer logic after code changes
- 🔁 Replay orders into downstream systems
- 🧪 Load historical data for testing or simulation
- 🧵 Filter replays by user, item, or status

Usage:
------
Replay all orders:
    python src/replay.py

Replay only for user 'alice':
    python src/replay.py --user alice

Replay 'pen' orders with status 'placed':
    python src/replay.py --item pen --status placed

Replay with delay between messages:
    python src/replay.py --delay 1.0
"""

import argparse
import json
import logging
import time
from confluent_kafka import SerializingProducer
import config

OUTPUT_FILE = "storage/orders.jsonl"


def load_orders(user=None, item=None, status=None):
    with open(OUTPUT_FILE) as f:
        for line in f:
            order = json.loads(line.strip())
            if user and order.get("user") != user:
                continue
            if item and order.get("item") != item:
                continue
            if status and order.get("status") != status:
                continue
            yield order


def create_producer():
    return SerializingProducer(
        {
            "bootstrap.servers": config.BOOTSTRAP_SERVERS,
            "key.serializer": config.get_key_serializer(),
            "value.serializer": config.get_value_serializer(),
        }
    )


def delivery_report(err, msg):
    if err:
        logging.error(f"❌ Delivery failed for {msg.key()}: {err}")
    else:
        logging.info(f"✅ Replayed {msg.key()} @ offset {msg.offset()}")


def replay_orders(delay, user, item, status):
    producer = create_producer()
    for order in load_orders(user=user, item=item, status=status):
        key = order["order_id"]
        producer.produce(
            topic=config.TOPIC,
            key=key,
            value=order,
            on_delivery=delivery_report,
        )
        producer.poll(0)
        time.sleep(delay)
    producer.flush()


def main():
    parser = argparse.ArgumentParser(description="Replay orders from orders.jsonl")
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between messages (seconds)"
    )
    parser.add_argument("--user", type=str, help="Replay only orders for this user")
    parser.add_argument("--item", type=str, help="Replay only orders for this item")
    parser.add_argument(
        "--status", type=str, help="Replay only orders with this status"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    replay_orders(args.delay, args.user, args.item, args.status)


if __name__ == "__main__":
    main()
