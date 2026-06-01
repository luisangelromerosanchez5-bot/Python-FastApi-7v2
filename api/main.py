import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from domain.entities import Base
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.entities.usuario import Usuario
from infrastructure.database.connection import SessionLocal, engine
from infrastructure.database.seed_data import seed_data
from api.controllers.auth_controller import router as auth_router
from api.controllers.companias_controller import router as companias_router
from api.controllers.empleados_controller import router as empleados_router
from api.middlewares.error_handler import register_error_handlers

app = FastAPI(
    title="API Companias y Empleados",
    description="API REST async con Onion Architecture + Repository Pattern + Unit of Work",
    version="2.0.0",
)

register_error_handlers(app)
app.include_router(auth_router)
app.include_router(companias_router)
app.include_router(empleados_router)


@app.on_event("startup")
async def startup():
    logger.info("Iniciando aplicacion async...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Esquemas de base de datos creados o verificados.")

        async with SessionLocal() as db:
            await seed_data(db)
        logger.info("Sembrado de datos finalizado.")
    except Exception as e:
        logger.error(f"Error durante la inicializacion del startup: {str(e)}", exc_info=True)
    logger.info("Aplicacion lista.")
