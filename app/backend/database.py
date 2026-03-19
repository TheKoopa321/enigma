import sqlite3

from config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rotor_left TEXT NOT NULL,
    rotor_middle TEXT NOT NULL,
    rotor_right TEXT NOT NULL,
    reflector TEXT NOT NULL,
    ring_left INTEGER DEFAULT 0,
    ring_middle INTEGER DEFAULT 0,
    ring_right INTEGER DEFAULT 0,
    position_left INTEGER DEFAULT 0,
    position_middle INTEGER DEFAULT 0,
    position_right INTEGER DEFAULT 0,
    plugboard TEXT DEFAULT '[]',
    created_by TEXT NOT NULL DEFAULT 'anonymous',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
"""


def _get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def get_configurations() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM configurations ORDER BY updated_at DESC",
        ).fetchall()
        return [dict(r) for r in rows]


def get_configuration(config_id: int) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM configurations WHERE id = ?", (config_id,)
        ).fetchone()
        return dict(row) if row else None


def save_configuration(data: dict, created_by: str = "anonymous") -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO configurations
               (name, rotor_left, rotor_middle, rotor_right, reflector,
                ring_left, ring_middle, ring_right,
                position_left, position_middle, position_right,
                plugboard, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["name"],
                data["rotor_left"],
                data["rotor_middle"],
                data["rotor_right"],
                data["reflector"],
                data.get("ring_left", 0),
                data.get("ring_middle", 0),
                data.get("ring_right", 0),
                data.get("position_left", 0),
                data.get("position_middle", 0),
                data.get("position_right", 0),
                data.get("plugboard", "[]"),
                created_by,
            ),
        )
        conn.commit()
        return cur.lastrowid


def delete_configuration(config_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM configurations WHERE id = ?", (config_id,))
        conn.commit()
        return cur.rowcount > 0
