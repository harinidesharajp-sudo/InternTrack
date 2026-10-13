"""
InternTrack Database Connector Module
Configured for MySQL with mysql.connector
Implements connection pooling, dictionary cursors, and helper execution functions.
"""

import os
import sqlite3
import logging

try:
    import mysql.connector
    from mysql.connector import pooling, Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InternTrackDB")

# Default MySQL connection configurations
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'interntrack'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4'
}

_connection_pool = None
_use_sqlite_fallback = False
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "interntrack_local.db")


def init_pool():
    """Initializes MySQL connection pool or flags fallback if unavailable."""
    global _connection_pool, _use_sqlite_fallback
    if MYSQL_AVAILABLE:
        try:
            # First ensure database exists
            temp_conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port']
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.close()
            temp_conn.close()

            # Initialize pool
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="interntrack_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG
            )
            _use_sqlite_fallback = False
            logger.info("Successfully connected to MySQL database: %s", DB_CONFIG['database'])
            return True
        except Exception as e:
            logger.warning("MySQL connection could not be established: %s", e)
            logger.warning("Falling back to embedded SQLite database for local demonstration.")
            _use_sqlite_fallback = True
            return False
    else:
        logger.warning("mysql-connector-python not installed; falling back to SQLite.")
        _use_sqlite_fallback = True
        return False


def get_connection():
    """Returns an active database connection."""
    global _connection_pool, _use_sqlite_fallback
    if _connection_pool is None and not _use_sqlite_fallback:
        init_pool()

    if not _use_sqlite_fallback and _connection_pool:
        try:
            return _connection_pool.get_connection()
        except Exception as e:
            logger.warning("Could not acquire connection from pool: %s. Using SQLite fallback.", e)
            _use_sqlite_fallback = True

    # Fallback SQLite connection
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _adapt_query_for_sqlite(query: str) -> str:
    """Adapts standard MySQL syntax to SQLite for seamless local execution."""
    adapted = query.replace("%s", "?")
    adapted = adapted.replace("AUTO_INCREMENT", "AUTOINCREMENT")
    adapted = adapted.replace("INT AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
    adapted = adapted.replace("DECIMAL(10,2)", "REAL")
    adapted = adapted.replace("DECIMAL(5,2)", "REAL")
    return adapted


def fetch_all(query: str, params: tuple = None):
    """
    Executes a SELECT query and returns all matching rows as dictionaries.
    
    :param query: SQL query string (uses %s placeholders)
    :param params: Tuple of query parameters
    :return: List of dicts representing rows
    """
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            sqlite_query = _adapt_query_for_sqlite(query)
            cursor = conn.cursor()
            if params:
                cursor.execute(sqlite_query, params)
            else:
                cursor.execute(sqlite_query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            cursor.close()
            return rows
    except Exception as err:
        logger.error("Error in fetch_all: %s | Query: %s", err, query)
        raise err
    finally:
        conn.close()


def fetch_one(query: str, params: tuple = None):
    """
    Executes a SELECT query and returns the first matching row as a dictionary.
    """
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query: str, params: tuple = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE query and commits the transaction.
    
    :param query: SQL query string
    :param params: Tuple of query parameters
    :return: Number of affected rows
    """
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            sqlite_query = _adapt_query_for_sqlite(query)
            cursor = conn.cursor()
            if params:
                cursor.execute(sqlite_query, params)
            else:
                cursor.execute(sqlite_query)
            affected = cursor.rowcount
            conn.commit()
            return affected
        else:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            affected = cursor.rowcount
            conn.commit()
            cursor.close()
            return affected
    except Exception as err:
        logger.error("Error in execute: %s | Query: %s", err, query)
        conn.rollback()
        raise err
    finally:
        conn.close()


def execute_lastrowid(query: str, params: tuple = None) -> int:
    """
    Executes an INSERT query and returns the auto-generated primary key ID.
    """
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            sqlite_query = _adapt_query_for_sqlite(query)
            cursor = conn.cursor()
            if params:
                cursor.execute(sqlite_query, params)
            else:
                cursor.execute(sqlite_query)
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        else:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return last_id
    except Exception as err:
        logger.error("Error in execute_lastrowid: %s | Query: %s", err, query)
        conn.rollback()
        raise err
    finally:
        conn.close()


def is_using_sqlite() -> bool:
    """Returns True if the system is currently using the local SQLite fallback."""
    return _use_sqlite_fallback
