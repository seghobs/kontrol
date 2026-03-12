import json
import sqlite3

from app_core.config import DB_FILE, EXEMPTIONS_FILE, TOKEN_FILE, TOKENS_FILE


def _connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            username TEXT PRIMARY KEY,
            full_name TEXT DEFAULT '',
            password TEXT DEFAULT '',
            token TEXT DEFAULT '',
            android_id_yeni TEXT DEFAULT '',
            user_agent TEXT DEFAULT '',
            device_id TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            added_at TEXT DEFAULT '',
            logout_reason TEXT DEFAULT '',
            logout_time TEXT DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS exemptions (
            post_link TEXT NOT NULL,
            username TEXT NOT NULL,
            PRIMARY KEY (post_link, username)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS key_value (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _row_to_token(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active", 0))
    if not item.get("logout_reason"):
        item.pop("logout_reason", None)
    if not item.get("logout_time"):
        item.pop("logout_time", None)
    return item


def _json_read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except Exception:
        return default


def _migrate_from_json(conn):
    existing_count = conn.execute("SELECT COUNT(*) AS c FROM tokens").fetchone()["c"]
    if existing_count > 0:
        return

    tokens_payload = _json_read(TOKENS_FILE, [])
    if isinstance(tokens_payload, list):
        for token in tokens_payload:
            conn.execute(
                """
                INSERT OR REPLACE INTO tokens (
                    username, full_name, password, token, android_id_yeni,
                    user_agent, device_id, is_active, added_at, logout_reason, logout_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token.get("username", ""),
                    token.get("full_name", ""),
                    token.get("password", ""),
                    token.get("token", ""),
                    token.get("android_id_yeni", ""),
                    token.get("user_agent", ""),
                    token.get("device_id", ""),
                    1 if token.get("is_active", False) else 0,
                    token.get("added_at", ""),
                    token.get("logout_reason", ""),
                    token.get("logout_time", ""),
                ),
            )

    exemptions_payload = _json_read(EXEMPTIONS_FILE, {})
    if isinstance(exemptions_payload, dict):
        for post_link, usernames in exemptions_payload.items():
            if not isinstance(usernames, list):
                continue
            for username in usernames:
                conn.execute(
                    "INSERT OR IGNORE INTO exemptions (post_link, username) VALUES (?, ?)",
                    (post_link, username),
                )

    token_payload = _json_read(TOKEN_FILE, {})
    if isinstance(token_payload, dict) and token_payload:
        conn.execute(
            "INSERT OR REPLACE INTO key_value (key, value) VALUES ('legacy_token_data', ?)",
            (json.dumps(token_payload, ensure_ascii=False),),
        )

    conn.commit()


def init_storage():
    conn = _connect()
    try:
        _init_db(conn)
        _migrate_from_json(conn)
    finally:
        conn.close()


def load_tokens():
    conn = _connect()
    try:
        _init_db(conn)
        rows = conn.execute("SELECT * FROM tokens ORDER BY rowid ASC").fetchall()
        return [_row_to_token(row) for row in rows]
    finally:
        conn.close()


def save_tokens(tokens):
    conn = _connect()
    try:
        _init_db(conn)
        conn.execute("DELETE FROM tokens")
        for token in tokens:
            conn.execute(
                """
                INSERT INTO tokens (
                    username, full_name, password, token, android_id_yeni,
                    user_agent, device_id, is_active, added_at, logout_reason, logout_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token.get("username", ""),
                    token.get("full_name", ""),
                    token.get("password", ""),
                    token.get("token", ""),
                    token.get("android_id_yeni", ""),
                    token.get("user_agent", ""),
                    token.get("device_id", ""),
                    1 if token.get("is_active", False) else 0,
                    token.get("added_at", ""),
                    token.get("logout_reason", ""),
                    token.get("logout_time", ""),
                ),
            )
        conn.commit()
        return True
    except Exception as error:
        print(f"Token DB yazma hatasi: {error}")
        return False
    finally:
        conn.close()


def load_exemptions():
    conn = _connect()
    try:
        _init_db(conn)
        rows = conn.execute("SELECT post_link, username FROM exemptions").fetchall()
        result = {}
        for row in rows:
            result.setdefault(row["post_link"], []).append(row["username"])
        return result
    finally:
        conn.close()


def save_exemptions(exemptions):
    conn = _connect()
    try:
        _init_db(conn)
        conn.execute("DELETE FROM exemptions")
        for post_link, usernames in exemptions.items():
            for username in usernames:
                conn.execute(
                    "INSERT OR IGNORE INTO exemptions (post_link, username) VALUES (?, ?)",
                    (post_link, username),
                )
        conn.commit()
        return True
    except Exception as error:
        print(f"Exemptions DB yazma hatasi: {error}")
        return False
    finally:
        conn.close()


def load_token_data():
    conn = _connect()
    try:
        _init_db(conn)
        row = conn.execute("SELECT value FROM key_value WHERE key='legacy_token_data'").fetchone()
        if not row:
            return {}
        try:
            return json.loads(row["value"])
        except Exception:
            return {}
    finally:
        conn.close()


def save_token_data(data):
    conn = _connect()
    try:
        _init_db(conn)
        conn.execute(
            "INSERT OR REPLACE INTO key_value (key, value) VALUES ('legacy_token_data', ?)",
            (json.dumps(data, ensure_ascii=False),),
        )
        conn.commit()
        return True
    except Exception as error:
        print(f"Legacy token DB yazma hatasi: {error}")
        return False
    finally:
        conn.close()
