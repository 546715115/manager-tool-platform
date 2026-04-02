"""
Models - SQLite Database Models for Tool Hub
"""

import sqlite3
from flask import g

DATABASE = 'tools.db'


def get_db():
    """Get database connection from Flask g object."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db(e=None):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database, create tools table if not exists."""
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cmd TEXT NOT NULL,
            port INTEGER NOT NULL,
            url TEXT,
            pid INTEGER,
            status TEXT DEFAULT 'stopped',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()


def get_all_tools():
    """Get all tools from database."""
    db = get_db()
    cursor = db.execute('SELECT * FROM tools ORDER BY id')
    tools = [dict(row) for row in cursor.fetchall()]
    return tools


def get_tool(id):
    """Get a single tool by ID."""
    db = get_db()
    cursor = db.execute('SELECT * FROM tools WHERE id = ?', (id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def create_tool(name, cmd, port, url=None):
    """Create a new tool."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO tools (name, cmd, port, url) VALUES (?, ?, ?, ?)',
        (name, cmd, port, url)
    )
    db.commit()
    return cursor.lastrowid


def update_tool(id, **kwargs):
    """Update a tool with given fields."""
    allowed_fields = ('name', 'cmd', 'port', 'url', 'pid', 'status')
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    set_clause = ', '.join(f'{key} = ?' for key in updates.keys())
    values = list(updates.values()) + [id]

    db = get_db()
    cursor = db.execute(f'UPDATE tools SET {set_clause} WHERE id = ?', values)
    db.commit()
    return cursor.rowcount > 0


def delete_tool(id):
    """Delete a tool by ID."""
    db = get_db()
    cursor = db.execute('DELETE FROM tools WHERE id = ?', (id,))
    db.commit()
    return cursor.rowcount > 0


def update_tool_status(id, status, pid=None):
    """Update tool status and optionally PID."""
    db = get_db()
    if pid is not None:
        db.execute(
            'UPDATE tools SET status = ?, pid = ? WHERE id = ?',
            (status, pid, id)
        )
    else:
        db.execute(
            'UPDATE tools SET status = ?, pid = NULL WHERE id = ?',
            (status, id)
        )
    db.commit()
    return True