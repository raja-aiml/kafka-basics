#!/usr/bin/env python3

import argparse
import csv
import os

FILE = "storage/users.csv"
FIELDS = ["user", "status"]


def load_users():
    if not os.path.exists(FILE):
        return []
    with open(FILE) as f:
        return list(csv.DictReader(f))


def save_users(rows):
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def show_users():
    rows = load_users()
    print("👥 Users:")
    for row in rows:
        print(f"• {row['user']} → {row['status']}")


def add_user(user, status):
    rows = load_users()
    if any(r["user"] == user for r in rows):
        print(f"⚠️ User '{user}' already exists. Use `update` instead.")
        return
    rows.append({"user": user, "status": status})
    save_users(rows)
    print(f"✅ Added user '{user}' with status '{status}'")


def update_user(user, status):
    rows = load_users()
    found = False
    for r in rows:
        if r["user"] == user:
            r["status"] = status
            found = True
    if not found:
        print(f"⚠️ User '{user}' not found.")
        return
    save_users(rows)
    print(f"✅ Updated user '{user}' to status '{status}'")


def main():
    parser = argparse.ArgumentParser(description="Manage users.csv")
    subparsers = parser.add_subparsers(dest="action")

    subparsers.add_parser("show")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--user", required=True)
    add_parser.add_argument("--status", required=True, choices=["paid", "unpaid"])

    upd_parser = subparsers.add_parser("update")
    upd_parser.add_argument("--user", required=True)
    upd_parser.add_argument("--status", required=True, choices=["paid", "unpaid"])

    args = parser.parse_args()

    if args.action == "show":
        show_users()
    elif args.action == "add":
        add_user(args.user, args.status)
    elif args.action == "update":
        update_user(args.user, args.status)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# python src/tool/user.py show
# python src/tool/user.py add --user dave --status paid
# python src/tool/user.py update --user bob --status paid
