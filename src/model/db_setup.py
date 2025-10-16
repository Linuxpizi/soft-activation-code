license_table = """
CREATE TABLE IF NOT EXISTS license (
    fingerprint TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL DEFAULT '',
    period INTEGER DEFAULT 0,
    gen_timestamp REAL NOT NULL DEFAULT 0.0,
    expire_timestamp REAL NOT NULL DEFAULT 0.0,
    license  TEXT NOT NULL DEFAULT '',
    UNIQUE (fingerprint)
);
"""
