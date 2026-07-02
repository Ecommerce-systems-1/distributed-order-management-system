import uuid
import aiosqlite
from typing import List, Dict, Any

class Database:
    def __init__(self, path: str = '/data/23_distributed_order_management_system.db'):
        self.path = path
        self._conn = None

    async def init(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute('PRAGMA journal_mode=WAL')
        await self._conn.executescript('''
            CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT DEFAULT 'pending', version INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
            CREATE TABLE IF NOT EXISTS order_events (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, event_type TEXT NOT NULL, payload TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT DEFAULT (datetime('now')));
            CREATE TABLE IF NOT EXISTS sagas (id TEXT PRIMARY KEY, order_id TEXT NOT NULL, saga_type TEXT NOT NULL, status TEXT DEFAULT 'started', current_step INTEGER DEFAULT 0, compensation_stack TEXT, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
        ''')
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()
