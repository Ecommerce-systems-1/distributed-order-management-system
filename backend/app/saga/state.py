import sqlite3, json
from datetime import datetime, timezone

class SagaState:
    STEP_NAMES = [
        (1, "InventoryService",   "reserve"),
        (2, "PaymentService",     "charge"),
        (3, "FulfillmentService", "route"),
        (4, "NotificationService","send"),
    ]

    @staticmethod
    def create_tables(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY, customer_id TEXT NOT NULL,
                customer_email TEXT NOT NULL, product_id TEXT NOT NULL,
                product_name TEXT NOT NULL, quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL, total_amount REAL NOT NULL,
                shipping_address TEXT NOT NULL,
                saga_status TEXT NOT NULL DEFAULT 'saga_started',
                fail_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS saga_steps (
                id TEXT PRIMARY KEY, order_id TEXT NOT NULL, step_number INTEGER NOT NULL,
                service_name TEXT NOT NULL, action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                input_data TEXT, output_data TEXT, error_message TEXT,
                started_at TEXT, completed_at TEXT, compensated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_saga_steps_order ON saga_steps(order_id, step_number);
        """)
        conn.commit()

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_order(self, order: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (order["id"], order["customer_id"], order["customer_email"],
             order["product_id"], order["product_name"], order["quantity"],
             order["unit_price"], order["total_amount"], order["shipping_address"],
             "running", order.get("fail_at"), now, now)
        )
        for step_num, svc_name, action in self.STEP_NAMES:
            self.conn.execute(
                "INSERT INTO saga_steps VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"{order['id']}_step_{step_num}", order["id"], step_num,
                 svc_name, action, "pending", None, None, None, None, None, None)
            )
        self.conn.commit()

    def update_step(self, order_id: str, step_number: int, **kwargs) -> None:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [order_id, step_number]
        self.conn.execute(f"UPDATE saga_steps SET {sets} WHERE order_id=? AND step_number=?", vals)
        self.conn.commit()

    def update_order_status(self, order_id: str, status: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("UPDATE orders SET saga_status=?, updated_at=? WHERE id=?",
                          (status, now, order_id))
        self.conn.commit()

    def get_steps(self, order_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM saga_steps WHERE order_id=? ORDER BY step_number",
            (order_id,)
        ).fetchall()
        return [dict(r) for r in rows]