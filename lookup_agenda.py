#!/usr/bin/env python3
# lookup_agenda.py

import argparse
import sys
from db_table import db_table

def print_rec(r):
    # tab-separated output
    print(
        f"{r['date']}\t"
        f"{r['time_start']}\t"
        f"{r['time_end']}\t"
        f"{r['title']}\t"
        f"{r['location']}\t"
        f"{r['description']}\t"
        f"{r['speaker']}"
    )

def lookup_agenda(field, term):
    valid = ["date","time_start","time_end","title","location","description","speaker"]
    if field not in valid:
        print(f"Error: choose from {valid}", file=sys.stderr)
        sys.exit(1)

    schema = {
        "id": "integer PRIMARY KEY",
        "parent_id": "integer",
        "date": "text",
        "time_start": "text",
        "time_end": "text",
        "title": "text",
        "location": "text",
        "description": "text",
        "speaker": "text"
    }

    tbl = db_table("sessions", schema)
    recs = tbl.select()
    tbl.close()

    q = term.lower().strip()
    parents = set()

    # find any session/subsession with term in the chosen field
    for r in recs:
        val = (r[field] or "").lower()
        if q in val:
            pid = r["parent_id"].strip()
            parents.add(int(pid) if pid else int(r["id"]))

    if not parents:
        print("No records found.")
        return

    # print each matching session and respective subsessions
    for pid in sorted(parents):
        # parent session
        parent = next((x for x in recs if int(x["id"]) == pid), None)
        if parent:
            print_rec(parent)
            # subsessions
            for sub in recs:
                if sub["parent_id"].strip() and int(sub["parent_id"]) == pid:
                    print_rec(sub)


def main():
    p = argparse.ArgumentParser(
        description="Lookup sessions by field (case-insensitive substring match)"
    )
    p.add_argument(
        "field",
        choices=["date","time_start","time_end","title","location","description","speaker"],
        help="Column to search"
    )
    p.add_argument("term", help="Substring to match")
    args = p.parse_args()
    lookup_agenda(args.field, args.term)


if __name__ == "__main__":
    main()