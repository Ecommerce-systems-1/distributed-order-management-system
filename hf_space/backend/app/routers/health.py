from fastapi import APIRouter, Depends
from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db=Depends(get_db)):
    rows = db.execute(
        "SELECT saga_status, COUNT(*) FROM orders GROUP BY saga_status"
    ).fetchall()
    stats = {r[0]: r[1] for r in rows}
    return {
        "status": "ok",
        "saga_stats": {
            "completed": stats.get("completed", 0),
            "failed": stats.get("failed", 0),
            "running": stats.get("running", 0),
        },
    }
