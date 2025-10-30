"""
Herramientas básicas del servidor MCP.

Contiene implementaciones de herramientas fundamentales como
calculadora, manipulación de texto y utilidades del sistema.
"""

import datetime
import os
import platform
import subprocess
from typing import Any, Dict

from .registry import ToolRegistry
from ..utils.logging import get_logger


logger = get_logger(__name__)


async def calculator_tool(operation: str, a: float, b: float = None) -> str:
    """
    Herramienta de calculadora básica.
    
    Args:
        operation: Operación a realizar (add, subtract, multiply, divide, sqrt, etc.)
        a: Primer número
        b: Segundo número (opcional para operaciones unarias)
        
    Returns:
        Resultado de la operación como string
    """
    try:
        if operation == "add":
            if b is None:
                raise ValueError("Se requiere segundo número para suma")
            result = a + b
        elif operation == "subtract":
            if b is None:
                raise ValueError("Se requiere segundo número para resta")
            result = a - b
        elif operation == "multiply":
            if b is None:
                raise ValueError("Se requiere segundo número para multiplicación")
            result = a * b
        elif operation == "divide":
            if b is None:
                raise ValueError("Se requiere segundo número para división")
            if b == 0:
                raise ValueError("División por cero no permitida")
            result = a / b
        elif operation == "sqrt":
            if a < 0:
                raise ValueError("No se puede calcular raíz cuadrada de número negativo")
            result = a ** 0.5
        elif operation == "power":
            if b is None:
                raise ValueError("Se requiere exponente para potencia")
            result = a ** b
        else:
            raise ValueError(f"Operación no soportada: {operation}")
        
        return f"Resultado: {result}"
    
    except Exception as e:
        logger.error("Calculator error", operation=operation, a=a, b=b, error=str(e))
        return f"Error: {str(e)}"


async def text_tool(action: str, text: str, **kwargs) -> str:
    """
    Herramienta de manipulación de texto.
    
    Args:
        action: Acción a realizar (upper, lower, reverse, count, etc.)
        text: Texto a procesar
        **kwargs: Argumentos adicionales según la acción
        
    Returns:
        Texto procesado
    """
    try:
        if action == "upper":
            return text.upper()
        elif action == "lower":
            return text.lower()
        elif action == "reverse":
            return text[::-1]
        elif action == "count":
            return f"Caracteres: {len(text)}, Palabras: {len(text.split())}"
        elif action == "replace":
            old_text = kwargs.get("old", "")
            new_text = kwargs.get("new", "")
            if not old_text:
                raise ValueError("Se requiere 'old' para reemplazar")
            return text.replace(old_text, new_text)
        elif action == "split":
            separator = kwargs.get("separator", " ")
            return ", ".join(text.split(separator))
        else:
            raise ValueError(f"Acción no soportada: {action}")
    
    except Exception as e:
        logger.error("Text tool error", action=action, error=str(e))
        return f"Error: {str(e)}"


async def system_info_tool() -> str:
    """
    Herramienta para obtener información del sistema.
    
    Returns:
        Información del sistema como string
    """
    try:
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "current_time": datetime.datetime.now().isoformat(),
            "working_directory": os.getcwd()
        }
        
        formatted_info = "\n".join([f"{key}: {value}" for key, value in info.items()])
        return f"Información del sistema:\n{formatted_info}"
    
    except Exception as e:
        logger.error("System info error", error=str(e))
        return f"Error obteniendo información del sistema: {str(e)}"


async def echo_tool(message: str) -> str:
    """
    Herramienta de eco simple.
    
    Args:
        message: Mensaje a repetir
        
    Returns:
        El mismo mensaje
    """
    return f"Echo: {message}"


async def register_basic_tools(registry: ToolRegistry) -> None:
    """
    Registra todas las herramientas básicas en el registro.
    
    Args:
        registry: Instancia del registro de herramientas
    """
    # Importar y registrar herramientas de deployment
    from .deployment.version_tools import register_version_tools
    from .deployment.deployment_tools import register_deployment_tools
    await register_version_tools(registry)
    await register_deployment_tools(registry)
    
    # Herramienta calculadora
    await registry.register_tool(
        name="calculator",
        description="Realiza operaciones matemáticas básicas",
        input_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "sqrt", "power"],
                    "description": "Operación matemática a realizar"
                },
                "a": {
                    "type": "number",
                    "description": "Primer número"
                },
                "b": {
                    "type": "number",
                    "description": "Segundo número (opcional para operaciones unarias)"
                }
            },
            "required": ["operation", "a"]
        },
        handler=calculator_tool
    )
    
    # Herramienta de texto
    await registry.register_tool(
        name="text_processor",
        description="Procesa y manipula texto de diversas formas",
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["upper", "lower", "reverse", "count", "replace", "split"],
                    "description": "Acción a realizar en el texto"
                },
                "text": {
                    "type": "string",
                    "description": "Texto a procesar"
                },
                "old": {
                    "type": "string",
                    "description": "Texto a reemplazar (para acción 'replace')"
                },
                "new": {
                    "type": "string",
                    "description": "Texto de reemplazo (para acción 'replace')"
                },
                "separator": {
                    "type": "string",
                    "description": "Separador para split (para acción 'split')"
                }
            },
            "required": ["action", "text"]
        },
        handler=text_tool
    )
    
    # Herramienta de información del sistema
    await registry.register_tool(
        name="system_info",
        description="Obtiene información del sistema operativo y entorno",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=system_info_tool
    )
    
    # Herramienta de eco
    await registry.register_tool(
        name="echo",
        description="Repite el mensaje proporcionado",
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Mensaje a repetir"
                }
            },
            "required": ["message"]
        },
        handler=echo_tool
    )
    
    logger.info("Basic and deployment tools registered successfully")