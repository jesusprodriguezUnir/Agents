"""
Implementación del servidor MCP (Model Context Protocol).

Este módulo contiene la implementación principal del servidor MCP
que maneja las conexiones de clientes y la ejecución de herramientas.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt, GetPromptRequest, GetPromptResult
from pydantic import BaseModel

from ..tools.registry import ToolRegistry
from ..schemas.mcp_protocol import MCPRequest, MCPResponse, MCPError
from ..utils.logging import setup_logging


logger = structlog.get_logger(__name__)


class MCPServer:
    """
    Servidor MCP principal que maneja la comunicación con clientes
    y la ejecución de herramientas registradas.
    """
    
    def __init__(self, name: str = "custom-mcp-server", version: str = "1.0.0"):
        """
        Inicializa el servidor MCP.
        
        Args:
            name: Nombre del servidor MCP
            version: Versión del servidor
        """
        self.name = name
        self.version = version
        self.server = Server(name, version)
        self.tool_registry = ToolRegistry()
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        """Configura los manejadores de eventos del servidor MCP."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Lista todas las herramientas disponibles."""
            logger.info("Listing available tools")
            return await self.tool_registry.list_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
            """
            Ejecuta una herramienta específica.
            
            Args:
                name: Nombre de la herramienta
                arguments: Argumentos para la herramienta
                
            Returns:
                Resultado de la ejecución de la herramienta
            """
            logger.info("Calling tool", tool_name=name, arguments=arguments)
            try:
                result = await self.tool_registry.execute_tool(name, arguments)
                logger.info("Tool executed successfully", tool_name=name)
                return result
            except Exception as e:
                logger.error("Tool execution failed", tool_name=name, error=str(e))
                raise
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """Lista todos los recursos disponibles."""
            logger.info("Listing available resources")
            return []  # Implementar según necesidades
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """Lista todos los prompts disponibles."""
            logger.info("Listing available prompts")
            return []  # Implementar según necesidades
    
    async def start(self) -> None:
        """Inicia el servidor MCP."""
        logger.info("Starting MCP server", name=self.name, version=self.version)
        
        # Registrar herramientas por defecto
        await self.tool_registry.register_default_tools()
        
        # Iniciar servidor
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def stop(self) -> None:
        """Detiene el servidor MCP."""
        logger.info("Stopping MCP server")
        # Implementar lógica de limpieza si es necesaria
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Obtiene información del servidor.
        
        Returns:
            Diccionario con información del servidor
        """
        return {
            "name": self.name,
            "version": self.version,
            "tools_count": len(self.tool_registry.tools),
            "status": "running"
        }


async def create_server() -> MCPServer:
    """
    Factory function para crear una instancia del servidor MCP.
    
    Returns:
        Instancia configurada del servidor MCP
    """
    # Configurar logging
    setup_logging()
    
    # Crear servidor
    server = MCPServer()
    
    logger.info("MCP server created successfully")
    return server


if __name__ == "__main__":
    async def main():
        """Función principal para ejecutar el servidor."""
        server = await create_server()
        try:
            await server.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await server.stop()
    
    asyncio.run(main())