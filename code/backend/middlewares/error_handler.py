import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.exceptions import AppError

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        message = "Erreur de validation."
        if exc.errors():
            erreur = exc.errors()[0]
            locs = [str(loc) for loc in erreur.get("loc", []) if loc not in ("body", "query", "path")]
            champ = ".".join(locs) if locs else ""
            err_type = erreur.get("err_type", "")
            if err_type == "missing":
                message = f"Le champ {champ} est manquant." if champ else "Un champ obligatoire est manquant."
            elif err_type in ("int_parsing", "int_type", "float_parsing", "float_type"):
                message = f"Le champ {champ} doit être un nombre valide." if champ else "Un champ numérique est invalide."
            elif err_type in ("bool_parsing", "bool_type"):
                message = f"Le champ {champ} doit être un booléen valide." if champ else "Un champ booléen est invalide."
            else:
                message = f"Le champ {champ} est invalide." if champ else "Les données fournies sont invalides."
        logger.warning(
            "endpoint=%s %s | exception=RequestValidationError | message=%s",
            request.method,
            request.url.path,
            message,
        )
        return JSONResponse(status_code=400, content={"error": message})

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning(
            "endpoint=%s %s | exception=%s | message=%s",
            request.method,
            request.url.path,
            exc.__class__.__name__,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception(
            "endpoint=%s %s | exception=%s",
            request.method,
            request.url.path,
            exc.__class__.__name__,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Une erreur interne est survenue"},
        )
