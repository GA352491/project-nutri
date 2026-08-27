"""
NutriPlan Unified Logger & Error Handling Middleware
====================================================
Provides standard structured logging and global exception handling with correlation IDs.
"""
import time
import uuid
import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s"


def configure_logging(service_name: str) -> logging.Logger:
    logger = logging.getLogger(f"nutriplan.{service_name}")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    log_dir = Path(os.getenv("LOG_DIR", str(Path(__file__).resolve().parents[4] / ".logs")))
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / f"{service_name.replace(' ', '_').lower()}.app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not attach file log handler at %s", log_dir)

    logger.propagate = False
    logging.getLogger().setLevel(logging.INFO)
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    return logger


def get_logger(service_name: str) -> logging.Logger:
    return configure_logging(service_name)

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every inbound request and outbound response with response times and correlation IDs.
    Catches unhandled exceptions and returns standardized error responses.
    """

    def __init__(self, app: FastAPI, service_name: str = "service") -> None:
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_logger(service_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        corr_id = request.headers.get("X-Correlation-ID") or f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Log request start
        client_ip = request.client.host if request.client else "unknown"
        self.logger.info(f"[{corr_id}] -> {request.method} {request.url.path} (from {client_ip})")

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            response.headers["X-Correlation-ID"] = corr_id
            response.headers["X-Response-Time-Ms"] = str(duration_ms)

            status_code = response.status_code
            if status_code >= 400:
                self.logger.warning(f"[{corr_id}] <- {status_code} {request.method} {request.url.path} ({duration_ms}ms)")
            else:
                self.logger.info(f"[{corr_id}] <- {status_code} {request.method} {request.url.path} ({duration_ms}ms)")

            return response

        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            err_msg = str(exc) or exc.__class__.__name__
            self.logger.error(f"[{corr_id}] !! 500 Unhandled Exception on {request.method} {request.url.path} ({duration_ms}ms): {err_msg}")
            self.logger.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again or contact support.",
                    "detail": err_msg,
                    "correlation_id": corr_id,
                    "service": self.service_name
                },
                headers={
                    "X-Correlation-ID": corr_id,
                    "X-Response-Time-Ms": str(duration_ms)
                }
            )
