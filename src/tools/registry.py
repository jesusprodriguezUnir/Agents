"""
Registro y gestión de herramientas MCP.

Este módulo maneja el registro, validación y ejecución de herramientas
disponibles en el servidor MCP.
"""

import asyncio
import inspect
import time
from typing import Any, Callable, Dict, List, Optional

from mcp.types import Tool
from pydantic import ValidationError

from ..schemas.mcp_protocol import ToolSchema, ToolExecutionResponse, MCPErrorCodes
from ..utils.logging import get_logger


logger = get_logger(__name__)


class ToolRegistry:
    """
    Registro central de herramientas MCP.
    
    Gestiona el registro, validación y ejecución de herramientas
    disponibles en el servidor.
    """
    
    def __init__(self):
        """Inicializa el registro de herramientas."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        
    async def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ) -> None:
        """
        Registra una nueva herramienta.
        
        Args:
            name: Nombre único de la herramienta
            description: Descripción de la funcionalidad
            input_schema: Esquema JSON para validar entrada
            handler: Función que ejecuta la herramienta
        """
        # Validar esquema de herramienta
        try:
            tool_schema = ToolSchema(
                name=name,
                description=description,
                input_schema=input_schema
            )
        except ValidationError as e:
            logger.error("Invalid tool schema", tool_name=name, error=str(e))
            raise ValueError(f"Invalid tool schema for {name}: {e}")
        
        # Validar que el handler es callable
        if not callable(handler):
            raise ValueError(f"Handler for tool {name} must be callable")
        
        # Registrar herramienta
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema
        }
        self._handlers[name] = handler
        
        logger.info("Tool registered successfully", tool_name=name)
    
    async def unregister_tool(self, name: str) -> bool:
        """
        Desregistra una herramienta.
        
        Args:
            name: Nombre de la herramienta a desregistrar
            
        Returns:
            True si se desregistró exitosamente, False si no existía
        """
        if name in self.tools:
            del self.tools[name]
            del self._handlers[name]
            logger.info("Tool unregistered", tool_name=name)
            return True
        return False
    
    async def list_tools(self) -> List[Tool]:
        """
        Lista todas las herramientas registradas.
        
        Returns:
            Lista de herramientas disponibles
        """
        return [
            Tool(
                name=tool_data["name"],
                description=tool_data["description"],
                inputSchema=tool_data["inputSchema"]
            )
            for tool_data in self.tools.values()
        ]
    
    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> List[Any]:
        """
        Ejecuta una herramienta específica.
        
        Args:
            name: Nombre de la herramienta
            arguments: Argumentos para la herramienta
            
        Returns:
            Resultado de la ejecución
            
        Raises:
            ValueError: Si la herramienta no existe
            Exception: Si la ejecución falla
        """
        if name not in self.tools:
            logger.error("Tool not found", tool_name=name)
            raise ValueError(f"Tool '{name}' not found")
        
        handler = self._handlers[name]
        start_time = time.time()
        
        try:
            # Validar argumentos según el esquema (implementación básica)
            # TODO: Implementar validación completa con jsonschema
            
            # Ejecutar herramienta
            if inspect.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = handler(**arguments)
            
            execution_time = time.time() - start_time
            
            logger.info(
                "Tool executed successfully",
                tool_name=name,
                execution_time=execution_time
            )
            
            # Convertir resultado a formato MCP
            if isinstance(result, list):
                return result
            else:
                return [{"type": "text", "text": str(result)}]
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Tool execution failed",
                tool_name=name,
                error=str(e),
                execution_time=execution_time
            )
            raise
    
    async def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de una herramienta.
        
        Args:
            name: Nombre de la herramienta
            
        Returns:
            Información de la herramienta o None si no existe
        """
        return self.tools.get(name)
    
    async def register_default_tools(self) -> None:
        """Registra las herramientas por defecto del servidor."""
        from .basic_tools import register_basic_tools
        await register_basic_tools(self)
        
        logger.info("Default tools registered", count=len(self.tools))
    
    def get_tools_count(self) -> int:
        """Retorna el número de herramientas registradas."""
        return len(self.tools)
    
    def get_tool_names(self) -> List[str]:
        """Retorna la lista de nombres de herramientas registradas."""
        return list(self.tools.keys())