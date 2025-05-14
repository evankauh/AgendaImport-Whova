#!/usr/bin/env python3
from db_table import db_table
import argparse
import os
import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        col.strip().lower()
        for col in df.columns
    ]

    return df


# Import Agenda excel -> define schema -> initialize data table
def import_schedule(excel_path: str, db_name: str):
    df = pd.read_excel(excel_path, skiprows=14, engine="xlrd")
    df = normalize_columns(df)

    schema = { 
        "id":             "integer PRIMARY KEY AUTOINCREMENT",
        "date":           "text NOT NULL",
        "time_start":     "text NOT NULL",
        "time_end":       "text NOT NULL",
        "session_title":  "text NOT NULL",
        "room_location":  "text",
        "description":    "text",
        "speakers":       "text",
        "is_subsession":  "integer NOT NULL DEFAULT 0",
        "parent_id":      "integer"
    }

    table = db_table("sessions", schema)

    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    


# Argument parsing
# excel_file (required)
# --db (optional; defaults to <excel_basename>.db)
def main():
    p = argparse.ArgumentParser(
        description="Import all sheets from an Excel file into SQLite"
    )

    p.add_argument(
        "excel_file",
        help="Path to the Excel file (must be .xls or .xlsx)"
    )

    p.add_argument(
        "--db", "-d",
        help="Path for the SQLite DB (defaults to EXCEL_BASE.db)",
        default=None
    )

    args = p.parse_args()

    if not os.path.isfile(args.excel_file):
        p.error(f"Excel file not found: {args.excel_file}")

    base = os.path.splitext(os.path.basename(args.excel_file))[0]
    sqlite_path = args.db or f"{base}.db"

    import_schedule(args.excel_file, sqlite_path)

if __name__ == "__main__":
    main()
