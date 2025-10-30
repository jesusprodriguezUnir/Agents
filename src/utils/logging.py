"""
Configuración de logging estructurado para el servidor MCP.

Proporciona configuración estandarizada de logging con soporte
para entornos de desarrollo y producción.
"""

import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(
    level: str = "INFO",
    format_json: bool = False,
    include_timestamp: bool = True
) -> None:
    """
    Configura el sistema de logging estructurado.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_json: Si True, formatea los logs como JSON
        include_timestamp: Si True, incluye timestamp en los logs
    """
    # Configurar logging básico de Python
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Configurar procesadores de structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="ISO"))
    
    # Agregar procesador de formato
    if format_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configurar structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Obtiene un logger estructurado para el módulo especificado.
    
    Args:
        name: Nombre del módulo o componente
        
    Returns:
        Logger estructurado configurado
    """
    return structlog.get_logger(name)


def log_request(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    params: Dict[str, Any],
    request_id: str
) -> None:
    """
    Registra una solicitud entrante.
    
    Args:
        logger: Logger a usar
        method: Método de la solicitud
        params: Parámetros de la solicitud
        request_id: ID de la solicitud
    """
    logger.info(
        "Incoming request",
        method=method,
        request_id=request_id,
        params_count=len(params) if params else 0
    )


def log_response(
    logger: structlog.stdlib.BoundLogger,
    request_id: str,
    success: bool,
    execution_time: float,
    error: str = None
) -> None:
    """
    Registra una respuesta de solicitud.
    
    Args:
        logger: Logger a usar
        request_id: ID de la solicitud
        success: Si la solicitud fue exitosa
        execution_time: Tiempo de ejecución en segundos
        error: Mensaje de error si hubo falla
    """
    if success:
        logger.info(
            "Request completed successfully",
            request_id=request_id,
            execution_time=execution_time
        )
    else:
        logger.error(
            "Request failed",
            request_id=request_id,
            execution_time=execution_time,
            error=error
        )


def log_tool_execution(
    logger: structlog.stdlib.BoundLogger,
    tool_name: str,
    arguments: Dict[str, Any],
    success: bool,
    execution_time: float,
    result: Any = None,
    error: str = None
) -> None:
    """
    Registra la ejecución de una herramienta.
    
    Args:
        logger: Logger a usar
        tool_name: Nombre de la herramienta
        arguments: Argumentos pasados a la herramienta
        success: Si la ejecución fue exitosa
        execution_time: Tiempo de ejecución en segundos
        result: Resultado de la ejecución (solo para debug)
        error: Mensaje de error si hubo falla
    """
    base_info = {
        "tool_name": tool_name,
        "execution_time": execution_time,
        "args_count": len(arguments) if arguments else 0
    }
    
    if success:
        logger.info("Tool executed successfully", **base_info)
    else:
        logger.error("Tool execution failed", error=error, **base_info)