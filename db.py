import sqlite3
import datetime
import os
from config import DB_FILENAME

def init_db():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT UNIQUE,
            author_name TEXT,
            article_title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_next_certificate_id(prefix="MIHS"):
    """
    Generates the next unique Certificate ID.
    prefix: "MIHS" = Human Studies journal; "ICSSHR" = International Conference on Social Sciences and Humanities Research.
    Format: MIHS-2026-000001 yoki ICSSHR-2026-000001.
    """
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    
    now = datetime.datetime.now()
    year = now.year
    prefix = f"{prefix}-{year}"

    # We want a global counter across all time? Or reset yearly? The example suggests global ID format implies year specific.
    # Let's count how many certificates exist for this year to generate the sequence number.
    # Actually, the user said: "Store last counter in SQLite so IDs never repeat."
    # If we restart the counter every year, IDs repeat (MIHS-2025-000001 vs MIHS-2026-000001).
    # Wait, the ID contains the year, so -000001 is fine if year changes. It's unique.
    
    query_prefix = f"{prefix}-%"
    # Use last ID to determine next sequence to avoid collisions if rows are deleted
    c.execute("SELECT certificate_id FROM certificates WHERE certificate_id LIKE ? ORDER BY id DESC LIMIT 1", (query_prefix,))
    result = c.fetchone()
    
    if result:
        last_id = result[0]
        # Extract sequence number e.g. MIHS-2026-000001 -> 1
        try:
            last_seq = int(last_id.split('-')[-1])
            next_seq = last_seq + 1
        except ValueError:
            # Fallback if format is weird
            next_seq = 1
    else:
        next_seq = 1
    
    # Format: MIHS-2026-000001
    cert_id = f"{prefix}-{next_seq:06d}"
    
    conn.close()
    return cert_id

def save_certificate(cert_id, author, title):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute("INSERT INTO certificates (certificate_id, author_name, article_title) VALUES (?, ?, ?)",
              (cert_id, author, title))
    conn.commit()
    conn.close()
