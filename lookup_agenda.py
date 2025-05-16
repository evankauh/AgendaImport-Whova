#!/usr/bin/env python3
# lookup_agenda.py

import argparse
import sys
from db_table import db_table

def print_rec(r, parent_sesh=None):
    # tab-separated output
    line = (
        f"{r['date']}\t"
        f"{r['time_start']}\t"
        f"{r['time_end']}\t"
        f"{r['title']}\t"
        f"{r['location']}\t"
        f"{r['description']}\t"
        f"{r['speaker']}"
    )
    if parent_sesh:
        line += f"\t(Subsession of: {parent_sesh})"
    print(line)

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
    children = set()  # ADDED: track subsessions that match directly

    for r in recs:
        val = (r[field] or "").lower()
        if q in val:
            if r["parent_id"].strip():
                children.add(int(r["id"]))    # ADDED
            else:
                parents.add(int(r["id"]))

    if not parents and not children:
        print("No records found.")
        return
    
    # map id→title for annotation
    id_map = { int(r["id"]): r["title"] for r in recs }  

    for r in recs:
        rid = int(r["id"])
        pid = r["parent_id"]

        if rid in parents:
            print_rec(r)
        elif pid and int(pid) in parents:
            print_rec(r, parent_sesh=id_map[int(pid)])
        elif rid in children:
            print_rec(r, parent_sesh=id_map[int(pid)])

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
