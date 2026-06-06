import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path

from core.runtime_config import MEMORY_DIR
from core.runtime_config import DATABASE_URL
from core.runtime_config import STORAGE_BACKEND


SQLITE_PATH = MEMORY_DIR / "helios_runtime.db"
store_lock = threading.Lock()


class ConnectionAdapter:
    def __init__(
        self,
        connection,
        postgres: bool = False
    ):
        self.connection = connection
        self.postgres = postgres

    def execute(
        self,
        query: str,
        params=()
    ):
        if self.postgres:
            query = query.replace(
                "BEGIN IMMEDIATE",
                "BEGIN"
            ).replace(
                "?",
                "%s"
            )
        return self.connection.execute(
            query,
            params
        )

    def __enter__(
        self
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback
    ):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
        return False


def _connect():
    if STORAGE_BACKEND == "postgres":
        if not DATABASE_URL:
            raise RuntimeError(
                "HELIOS_DATABASE_URL is required for postgres storage."
            )
        import psycopg

        connection = ConnectionAdapter(
            psycopg.connect(
                DATABASE_URL
            ),
            postgres=True
        )
    else:
        MEMORY_DIR.mkdir(
            parents=True,
            exist_ok=True
        )
        raw_connection = sqlite3.connect(
            SQLITE_PATH,
            timeout=10
        )
        raw_connection.execute(
            "PRAGMA journal_mode=WAL"
        )
        raw_connection.execute(
            "PRAGMA busy_timeout=10000"
        )
        connection = ConnectionAdapter(
            raw_connection
        )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS runtime_documents (
            name TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rate_limit_hits (
            bucket TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS rate_limit_hits_idx
        ON rate_limit_hits(bucket, created_at)
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS worker_jobs (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            lease_owner TEXT,
            lease_until REAL,
            result TEXT,
            error TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS worker_jobs_status_idx
        ON worker_jobs(status, lease_until, created_at)
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_memories (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )

    return connection


def load_document(
    name: str,
    fallback
):
    if STORAGE_BACKEND not in {
        "sqlite",
        "postgres"
    }:
        return fallback

    with store_lock:
        try:
            with _connect() as connection:
                row = connection.execute(
                    "SELECT payload FROM runtime_documents WHERE name = ?",
                    (
                        name,
                    )
                ).fetchone()

            if not row:
                return fallback

            return json.loads(
                row[0]
            )

        except Exception:
            return fallback


def save_document(
    name: str,
    payload
) -> bool:
    if STORAGE_BACKEND not in {
        "sqlite",
        "postgres"
    }:
        return False

    with store_lock:
        try:
            serialized = json.dumps(
                payload,
                ensure_ascii=False
            )

            with _connect() as connection:
                connection.execute(
                    """
                    INSERT INTO runtime_documents (name, payload, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(name) DO UPDATE SET
                        payload = excluded.payload,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        name,
                        serialized
                    )
                )

            return True

        except Exception:
            return False


def storage_status():
    return {
        "backend": STORAGE_BACKEND,
        "sqlite_path": str(
            SQLITE_PATH
        )
        if STORAGE_BACKEND == "sqlite"
        else None,
        "database_url_configured": bool(
            DATABASE_URL
        )
        if STORAGE_BACKEND == "postgres"
        else None,
        "durable": STORAGE_BACKEND in {
            "sqlite",
            "postgres"
        },
        "multi_worker": STORAGE_BACKEND == "postgres"
    }


def enqueue_job(
    kind: str,
    payload
) -> dict:
    job_id = str(
        uuid.uuid4()
    )
    now = time.time()
    with store_lock:
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO worker_jobs (
                    id, kind, payload, status, created_at, updated_at
                ) VALUES (?, ?, ?, 'queued', ?, ?)
                """,
                (
                    job_id,
                    kind,
                    json.dumps(
                        payload,
                        ensure_ascii=False
                    ),
                    now,
                    now
                )
            )
    return get_job(
        job_id
    )


def get_job(
    job_id: str
) -> dict | None:
    with store_lock:
        with _connect() as connection:
            row = connection.execute(
                """
                SELECT id, kind, payload, status, attempts, lease_owner,
                       lease_until, result, error, created_at, updated_at
                FROM worker_jobs WHERE id = ?
                """,
                (
                    job_id,
                )
            ).fetchone()

    if not row:
        return None
    keys = (
        "id",
        "kind",
        "payload",
        "status",
        "attempts",
        "lease_owner",
        "lease_until",
        "result",
        "error",
        "created_at",
        "updated_at"
    )
    job = dict(
        zip(
            keys,
            row
        )
    )
    for field in (
        "payload",
        "result"
    ):
        if job.get(
            field
        ):
            try:
                job[field] = json.loads(
                    job[field]
                )
            except Exception:
                pass
    return job


def claim_job(
    worker_id: str,
    lease_seconds: int,
    kinds: list[str] | None = None
) -> dict | None:
    now = time.time()
    kinds = kinds or []
    with store_lock:
        with _connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )
            params = [
                now
            ]
            kind_clause = ""
            if kinds:
                placeholders = ",".join(
                    "?"
                    for _ in kinds
                )
                kind_clause = f" AND kind IN ({placeholders})"
                params.extend(
                    kinds
                )
            lock_clause = (
                "FOR UPDATE SKIP LOCKED"
                if STORAGE_BACKEND == "postgres"
                else ""
            )
            row = connection.execute(
                f"""
                SELECT id FROM worker_jobs
                WHERE (
                    status = 'queued'
                    OR (status = 'running' AND lease_until < ?)
                )
                {kind_clause}
                ORDER BY created_at ASC
                LIMIT 1
                {lock_clause}
                """,
                params
            ).fetchone()
            if not row:
                return None
            job_id = row[0]
            connection.execute(
                """
                UPDATE worker_jobs
                SET status = 'running',
                    attempts = attempts + 1,
                    lease_owner = ?,
                    lease_until = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    worker_id,
                    now + lease_seconds,
                    now,
                    job_id
                )
            )
    return get_job(
        job_id
    )


def complete_job(
    job_id: str,
    worker_id: str,
    result=None,
    error: str | None = None
) -> dict | None:
    now = time.time()
    status = "failed" if error else "completed"
    with store_lock:
        with _connect() as connection:
            connection.execute(
                """
                UPDATE worker_jobs
                SET status = ?, result = ?, error = ?, lease_until = NULL,
                    updated_at = ?
                WHERE id = ? AND lease_owner = ?
                """,
                (
                    status,
                    json.dumps(
                        result,
                        ensure_ascii=False
                    )
                    if result is not None
                    else None,
                    error,
                    now,
                    job_id,
                    worker_id
                )
            )
    return get_job(
        job_id
    )


def list_jobs(
    limit: int = 50
) -> list[dict]:
    with store_lock:
        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT id FROM worker_jobs
                ORDER BY created_at DESC LIMIT ?
                """,
                (
                    max(
                        1,
                        min(
                            limit,
                            200
                        )
                    ),
                )
            ).fetchall()
    return [
        job
        for row in rows
        if (
            job := get_job(
                row[0]
            )
        )
    ]


def upsert_semantic_memory(
    memory_id: str,
    text: str,
    embedding: list[float],
    metadata: dict | None = None
) -> None:
    now = time.time()
    with store_lock:
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO semantic_memories (
                    id, text, embedding, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    text = excluded.text,
                    embedding = excluded.embedding,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at
                """,
                (
                    memory_id,
                    text,
                    json.dumps(
                        embedding
                    ),
                    json.dumps(
                        metadata or {},
                        ensure_ascii=False
                    ),
                    now,
                    now
                )
            )


def load_semantic_memories() -> list[dict]:
    with store_lock:
        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT id, text, embedding, metadata, created_at, updated_at
                FROM semantic_memories
                """
            ).fetchall()
    return [
        {
            "id": row[0],
            "text": row[1],
            "embedding": json.loads(
                row[2]
            ),
            "metadata": json.loads(
                row[3]
            ),
            "created_at": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]


def allow_rate_limited_request(
    bucket: str,
    limit: int,
    window_seconds: int = 60
) -> bool:
    now = time.time()
    cutoff = now - window_seconds
    with store_lock:
        with _connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )
            connection.execute(
                "DELETE FROM rate_limit_hits WHERE created_at < ?",
                (
                    cutoff,
                )
            )
            count = connection.execute(
                """
                SELECT COUNT(*) FROM rate_limit_hits
                WHERE bucket = ? AND created_at >= ?
                """,
                (
                    bucket,
                    cutoff
                )
            ).fetchone()[0]
            if count >= limit:
                return False
            connection.execute(
                """
                INSERT INTO rate_limit_hits(bucket, created_at)
                VALUES (?, ?)
                """,
                (
                    bucket,
                    now
                )
            )
    return True
"# Performance Note: Remove global store_lock and rely on WAL mode for SQLite."
