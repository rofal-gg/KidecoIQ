"""
Wait for PostgreSQL to be ready before starting the application.
Usage: python wait_for_db.py <database_url>
"""

import sys
import time

from sqlalchemy import create_engine, text


def wait_for_db(url: str, max_retries: int = 30, sleep_sec: int = 1):
    print(f"Waiting for database at: {url}", flush=True)
    engine = create_engine(url)

    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready!", flush=True)
            engine.dispose()
            return True
        except Exception as e:
            print(f"  Attempt {attempt}/{max_retries}: DB not ready yet — {e}", flush=True)
            time.sleep(sleep_sec)

    print("ERROR: Database not ready after maximum retries.", flush=True)
    engine.dispose()
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wait_for_db.py <DATABASE_URL>")
        sys.exit(1)

    url = sys.argv[1]
    success = wait_for_db(url)
    sys.exit(0 if success else 1)
