#!/usr/bin/env python3
import argparse
import sys
import sqlite3

import pandas as pd
from db_table import db_table

def normalize_header(label: str) -> str:
    s = (label or "").strip()

    if s.startswith("*"):
        s = s[1:]

    s = s.lower()

    for ch in ("\n", "/", "-", "(", ")"):
        s = s.replace(ch, " ")

    key = "_".join(s.split())

    if key == "date": return "date"
    if "time" in key and "start" in key: return "time_start"
    if "time" in key and "end" in key: return "time_end"
    if "session" in key and "title" in key: return "title"
    if "location" in key: return "location"
    if "description" in key: return "description"
    if "speaker" in key: return "speaker"

    return None

def import_schedule(excel_path: str):
    # drop old table so schema changes apply
    conn = sqlite3.connect(db_table.DB_NAME)
    conn.execute("DROP TABLE IF EXISTS sessions")  # EDITED: fixed syntax
    conn.commit()
    conn.close()

    SCHEMA = {
        "id":           "integer PRIMARY KEY",
        "parent_id":    "integer",
        "date":         "text",
        "time_start":   "text",
        "time_end":     "text",
        "title":        "text",
        "location":     "text",
        "description":  "text",
        "speaker":      "text",
    }
    table = db_table("sessions", SCHEMA)

    # read the sheet: header is on Excel row 15 → pandas index 14
    raw = pd.read_excel(excel_path, header=None, dtype=str)
    header_idx = 14

    # build map from fixed header row col to idx
    header_row = raw.iloc[header_idx].fillna("").tolist()
    col_map = {}
    type_idx = None  
    for idx, raw_label in enumerate(header_row):
        field = normalize_header(raw_label)
        if field and field not in col_map:
            col_map[field] = idx
        low = (raw_label or "").lower()
        if "sub" in low and "session" in low and type_idx is None:
            type_idx = idx

    required = ["date","time_start","time_end","title","location","description","speaker"]

    current_parent = None
    for _, row in raw.iloc[header_idx+1:].iterrows():
        cells = row.fillna("").astype(str).str.strip().tolist()

        type = cells[type_idx].lower() if type_idx is not None else ""
        is_sub = (type == "sub")

        rec = {
            field: cells[col_map[field]].replace("'", "''")
            for field in required
        }

        if not is_sub:
            item = {"parent_id": "", **rec}
            current_parent = table.insert(item)
        else:
            # sub-session of last parent
            item = {"parent_id": str(current_parent), **rec}
            table.insert(item)

    table.close()
    print("import done")

def main():
    p = argparse.ArgumentParser(
        description="import agenda into sqlite"
    )
    p.add_argument("excel_file", help="path to the agenda.xls file")
    args = p.parse_args()
    import_schedule(args.excel_file)

if __name__ == "__main__":
    main()
