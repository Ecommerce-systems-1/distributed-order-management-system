    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from app.database import init_db
    from app.saga.state import SagaState
    from app.routers import orders, products, health
    import pathlib

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        conn = init_db()
        SagaState.create_tables(conn)
        app.state.db = conn
        yield

    app = FastAPI(title="Distributed OMS", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(orders.router)
    app.include_router(products.router)
    app.include_router(health.router)
    static_dir = pathlib.Path("/app/frontend/out")
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")