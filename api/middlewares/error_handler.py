import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

logger = logging.getLogger(__name__)

def register_error_handlers(app: FastAPI):
    """Registra los manejadores globales de excepciones en la aplicación FastAPI."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTPException en {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "detail": None
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"RequestValidationError en {request.url.path}: {exc.errors()}")
        
        errors = exc.errors()
        message = "Error de validación en los datos de la solicitud."
        
        # Detectar si el cuerpo (body) está completamente ausente o si se envió en formato incorrecto (ej. bytes)
        is_body_missing = any(error.get("loc") == ("body",) and error.get("type") == "missing" for error in errors)
        is_body_wrong_type = any(error.get("loc") == ("body",) and "model_attributes_type" in error.get("type", "") for error in errors)
        
        if is_body_missing or is_body_wrong_type:
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type.lower():
                message = "El cuerpo de la solicitud JSON es requerido. Asegúrate de configurar la cabecera 'Content-Type: application/json' y enviar los datos correspondientes en el cuerpo de la petición."
            else:
                message = "El cuerpo de la solicitud está vacío o no es un JSON válido. Asegúrate de enviar un cuerpo JSON estructurado con los campos obligatorios."
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status": "error",
                "message": message,
                "detail": errors
            })
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(f"Pydantic ValidationError en {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status": "error",
                "message": "Error de validación interna en los modelos de datos.",
                "detail": exc.errors()
            })
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Error inesperado 500: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Ha ocurrido un error inesperado en el servidor.",
                "detail": None
            }
        )
