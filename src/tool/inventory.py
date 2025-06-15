#!/usr/bin/env python3

import argparse
import csv
import os

FILE = "storage/inventory.csv"
FIELDS = ["item", "quantity"]


def load_inventory():
    if not os.path.exists(FILE):
        return []
    with open(FILE) as f:
        return list(csv.DictReader(f))


def save_inventory(rows):
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def show_inventory():
    rows = load_inventory()
    print("📦 Inventory:")
    for row in rows:
        print(f"• {row['item']} → {row['quantity']}")


def add_item(item, quantity):
    rows = load_inventory()
    if any(r["item"] == item for r in rows):
        print(f"⚠️ Item '{item}' already exists. Use `update` instead.")
        return
    rows.append({"item": item, "quantity": str(quantity)})
    save_inventory(rows)
    print(f"✅ Added item '{item}' with quantity {quantity}")


def update_item(item, quantity):
    rows = load_inventory()
    found = False
    for r in rows:
        if r["item"] == item:
            r["quantity"] = str(quantity)
            found = True
    if not found:
        print(f"⚠️ Item '{item}' not found.")
        return
    save_inventory(rows)
    print(f"✅ Updated item '{item}' to quantity {quantity}")


def main():
    parser = argparse.ArgumentParser(description="Manage inventory.csv")
    subparsers = parser.add_subparsers(dest="action")

    subparsers.add_parser("show")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--item", required=True)
    add_parser.add_argument("--quantity", type=int, required=True)

    upd_parser = subparsers.add_parser("update")
    upd_parser.add_argument("--item", required=True)
    upd_parser.add_argument("--quantity", type=int, required=True)

    args = parser.parse_args()

    if args.action == "show":
        show_inventory()
    elif args.action == "add":
        add_item(args.item, args.quantity)
    elif args.action == "update":
        update_item(args.item, args.quantity)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# python src/tool/inventory.py show
# python src/tool/inventory.py add --item laptop --quantity 10
# python src/tool/inventory.py update --item pen --quantity 25
