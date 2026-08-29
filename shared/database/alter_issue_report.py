import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

alter = """
ALTER TABLE ProductIssue ADD COLUMN resolved_value TEXT DEFAULT NULL;
"""
cursor.execute(alter)

alter = """
ALTER TABLE ProductReportItem DROP COLUMN proposed_value_outcome;
"""
cursor.execute(alter)

conn.commit()
conn.close()