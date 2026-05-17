"""Centralized logging configuration for TalentFlow AI backend."""

import datetime
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        return ct.strftime("%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        for attr in [
            "run_id",
            "trace_id",
            "stage",
            "duration_ms",
            "error_code",
            "status_code",
            "request_id",
            "client_ip",
            "path",
            "method",
        ]:
            if hasattr(record, attr):
                log_obj[attr] = getattr(record, attr)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class TextFormatter(logging.Formatter):
    """Readable console formatter."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        return ct.strftime("%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        base = f"[{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}] {record.levelname}: {record.getMessage()}"

        custom_parts = []
        for attr in [
            "run_id",
            "trace_id",
            "stage",
            "duration_ms",
            "error_code",
            "status_code",
            "request_id",
            "client_ip",
            "path",
            "method",
        ]:
            if hasattr(record, attr):
                custom_parts.append(f"{attr}={getattr(record, attr)}")

        if custom_parts:
            base += " (" + ", ".join(custom_parts) + ")"

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


def configure_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    environment = os.getenv("ENVIRONMENT", "development").lower()
    log_file_path = os.getenv("LOG_FILE_PATH", "/var/log/talentflow")

    formatter = JsonFormatter() if log_format == "json" else TextFormatter()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    root_logger.addHandler(console_handler)

    if environment != "development":
        try:
            os.makedirs(log_file_path, exist_ok=True)

            app_log_handler = RotatingFileHandler(
                os.path.join(log_file_path, "app.log"),
                maxBytes=100 * 1024 * 1024,
                backupCount=10,
            )
            app_log_handler.setFormatter(formatter)
            app_log_handler.setLevel(getattr(logging, log_level, logging.INFO))
            root_logger.addHandler(app_log_handler)

            error_log_handler = RotatingFileHandler(
                os.path.join(log_file_path, "error.log"),
                maxBytes=50 * 1024 * 1024,
                backupCount=5,
            )
            error_log_handler.setFormatter(formatter)
            error_log_handler.setLevel(logging.ERROR)
            root_logger.addHandler(error_log_handler)
        except Exception as exc:
            root_logger.warning("Failed to configure file logging: %s", exc)

    root_logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_format": log_format,
            "environment": environment,
        },
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
