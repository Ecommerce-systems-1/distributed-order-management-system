# Data Model — Distributed Order Management System

```sql
CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT DEFAULT 'pending', version INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
```
