from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class Memory:

    def __init__(self, database_path: Optional[str] = None):

        if database_path is None:
            database_path = str(
                Path(__file__).resolve().parent / "memory.db"
            )

        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

    @staticmethod
    def _timestamp() -> str:

        return datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

    def save(self, content: str) -> int:

        content = content.strip()

        if not content:
            raise ValueError(
                "Memory content cannot be empty."
            )

        timestamp = self._timestamp()

        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO memories (
                    content,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    content,
                    timestamp,
                    timestamp
                )
            )

            connection.commit()

            return int(cursor.lastrowid)

    def get(self, memory_id: int) -> Optional[dict]:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    id,
                    content,
                    created_at,
                    updated_at
                FROM memories
                WHERE id = ?
                """,
                (memory_id,)
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_all(self) -> list[dict]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    content,
                    created_at,
                    updated_at
                FROM memories
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def search(self, query: str) -> list[dict]:

        query = query.strip()

        if not query:
            return []

        pattern = f"%{query}%"

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    content,
                    created_at,
                    updated_at
                FROM memories
                WHERE content LIKE ?
                ORDER BY id DESC
                """,
                (pattern,)
            ).fetchall()

        return [dict(row) for row in rows]

    def delete(self, memory_id: int) -> bool:

        with self._connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE id = ?
                """,
                (memory_id,)
            )

            connection.commit()

            return cursor.rowcount > 0

    def delete_matching(self, query: str) -> int:

        query = query.strip()

        if not query:
            return 0

        pattern = f"%{query}%"

        with self._connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE content LIKE ?
                """,
                (pattern,)
            )

            connection.commit()

            return cursor.rowcount

    def clear(self) -> int:

        with self._connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM memories
                """
            )

            connection.commit()

            return cursor.rowcount

    def count(self) -> int:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM memories
                """
            ).fetchone()

        return int(row["count"])

    def update(
        self,
        memory_id: int,
        content: str
    ) -> bool:

        content = content.strip()

        if not content:
            raise ValueError(
                "Memory content cannot be empty."
            )

        timestamp = self._timestamp()

        with self._connect() as connection:

            cursor = connection.execute(
                """
                UPDATE memories
                SET
                    content = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    content,
                    timestamp,
                    memory_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0


memory = Memory()


def save_memory(content: str) -> int:
    return memory.save(content)


def search_memory(query: str) -> list[dict]:
    return memory.search(query)


def get_memories() -> list[dict]:
    return memory.get_all()


def delete_memory(memory_id: int) -> bool:
    return memory.delete(memory_id)


def clear_memory() -> int:
    return memory.clear()


def memory_count() -> int:
    return memory.count()