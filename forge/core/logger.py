import logging
import structlog
from forge.config.settings import settings
from forge.core.context import get_request_id, get_tenant_id


def add_forge_context(logger, method_name, event_dict):
    event_dict["request_id"] = get_request_id()
    tenant = get_tenant_id()
    if tenant:
        event_dict["tenant_id"] = tenant
    return event_dict


def setup_logging() -> None:
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_forge_context,
    ]

    if settings.debug:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
