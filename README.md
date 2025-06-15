---
# Event Streaming Platform with Python and Apache Kafka

This project provides a hands-on demonstration of a complete event-driven system built on **Apache Kafka** and the **Confluent Platform**. It showcases how to implement **Python-based producers and consumers** to process a stream of order events, apply business logic against stateful data, and manage the system's state using simple command-line tools.

---
## 🏛️ Architecture

The system follows a classic event streaming pattern where a producer sends order events to a Kafka topic. A consumer then processes these events, validates them against user and inventory data, and persists the successful orders.

### High-Level Flow

```
[ User & Inventory Data (storage/*.csv) ]
                 |
                 ▼
+-----------------------------------+
|        Python Producer            | ━(sends Avro-encoded events)━▶ [ Kafka Topic: "orders" ]
| (src/prodcuer.py)                 |                                         |
+-----------------------------------+                                         |
                                                                              ▼
                                                       +-----------------------------------+
                                                       |        Python Consumer            |
                                                       | (src/consumer.py)                 |
                                                       |  - Fetches and validates orders   |
                                                       |  - Applies business logic         |
                                                       +-----------------------------------+
                                                                        |
                                                                        ▼
                                                       [ Processed Orders (storage/orders.jsonl) ]
```

---
## 🚀 Getting Started

Follow these steps to set up and run the entire system on your local machine.

### Prerequisites

* **Docker & Docker Compose**: Required to run the Confluent Platform stack.
* **Python 3.12+**: Required for the producer, consumer, and CLI tools.
* **Poetry or UV**: For managing Python dependencies (as defined in `pyproject.toml`).

### Setup and Execution

#### Start the Confluent Environment

Launch the entire Confluent Platform stack using Docker Compose. This includes Kafka, Schema Registry, Control Center, and more.

```bash
docker compose -f deploy/docker/docker-compose.yml up -d
```

You can monitor the stack via the **Confluent Control Center** at `http://localhost:9021`.

#### Bootstrap Initial Data

Before running the system, populate the CSV files with some initial user and inventory data using the provided CLI tools.

**Create Users:**

```bash
# Add users with different payment statuses
python src/tool/user.py add --user alice --status paid
python src/tool/user.py add --user bob --status unpaid
python src/tool/user.py add --user carol --status paid
```

**Add Inventory:**

```bash
# Add initial stock for various items
python src/tool/inventory.py add --item book --quantity 10
python src/tool/inventory.py add --item pen --quantity 50
python src/tool/inventory.py add --item notebook --quantity 20
```

#### Run the Producer and Consumer

With the environment running and data bootstrapped, you can start the event flow.

**Start the Producer (in a new terminal):**
This script generates sample orders and sends them to the `orders` Kafka topic.

```bash
# Send 5 sample orders with a 1-second delay between each
python src/prodcuer.py --count 5 --delay 1
```

**Start the Consumer (in another terminal):**
This script listens for new messages on the `orders` topic, processes them, and writes valid orders to `storage/orders.jsonl`.

```bash
python src/consumer.py
```
You can reset consumer offsets on startup using `--reset` and optionally
`--partitions` and `--reset-to`:

```bash
python src/consumer.py consume --reset --reset-to latest
```

**Replay Processed Orders (optional):**
Use `src/replay.py` to resend orders from `storage/orders.jsonl` back into Kafka.

```bash
python src/replay.py --delay 0.5
```

---
## ⚙️ Business Logic

The consumer script (`src/consumer.py`) contains the core business logic. For each order event received, it performs the following validations before processing:

* **User Status Check**: It verifies that the user exists in `storage/users.csv` and has a `paid` status.
* **Inventory Check**: It confirms that the requested item exists in `storage/inventory.csv` and has sufficient quantity in stock.

✅ **If both checks pass**: The order is considered valid. The consumer deducts the ordered quantity from the inventory and appends the order details to `storage/orders.jsonl`.
❌ **If either check fails**: The order is rejected, and a warning is logged to the console. The inventory and order log remain unchanged.

---
## 🛠️ CLI Tools

The project includes simple command-line tools to manage the user and inventory data stored in the CSV files.

### Manage Users (`src/tool/user.py`)

| Command | Description                  | Example                               |
| :------ | :--------------------------- | :------------------------------------ |
| `show`  | Display all users and statuses. | `python src/tool/user.py show`        |
| `add`   | Add a new user.              | `python src/tool/user.py add --user dave --status paid` |
| `update` | Update an existing user's status. | `python src/tool/user.py update --user bob --status paid` |

### Manage Inventory (`src/tool/inventory.py`)

| Command | Description                  | Example                               |
| :------ | :--------------------------- | :------------------------------------ |
| `show`  | Display all items and quantities. | `python src/tool/inventory.py show`   |
| `add`   | Add a new item to inventory. | `python src/tool/inventory.py add --item laptop --quantity 5` |
| `update` | Update an existing item's quantity. | `python src/tool/inventory.py update --item pen --quantity 100` |

---
## 🗂️ Project Structure

```
kafka-basics/
├── src/                      # Python source code
│   ├── consumer.py           # Kafka consumer with business logic
│   ├── prodcuer.py           # Kafka producer to generate sample orders
│   ├── replay.py             # Utility to replay processed orders
│   ├── service/
│   │   └── order_processor.py
│   ├── data/
│   │   ├── inventory.py
│   │   └── users.py
│   ├── kafka_utils/
│   │   └── offset_reset.py
│   └── tool/
│       ├── inventory.py
│       └── user.py
├── storage/                  # Data files (mutable state)
│   ├── users.csv             # User data and payment status
│   ├── inventory.csv         # Item inventory and quantities
│   └── orders.jsonl          # Persisted log of successful orders
├── deploy/docker/            # Docker Compose setup for Confluent Platform
│   └── docker-compose.yml
├── pyproject.toml            # Poetry/UV project and dependency definition
└── README.md                 # This documentation
```
