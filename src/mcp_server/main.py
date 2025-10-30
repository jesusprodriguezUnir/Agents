"""
Punto de entrada principal para el servidor MCP.

Este módulo inicializa y ejecuta el servidor MCP con todas
las configuraciones necesarias.
"""

import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.mcp_server.server import create_server
from src.utils.logging import setup_logging, get_logger


async def main():
    """
    Función principal que inicializa y ejecuta el servidor MCP.
    """
    # Configurar logging
    setup_logging(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format_json=os.getenv("LOG_FORMAT", "").lower() == "json"
    )
    
    logger = get_logger(__name__)
    logger.info("Starting MCP Server application")
    
    try:
        # Crear y configurar servidor
        server = await create_server()
        
        # Ejecutar servidor
        logger.info("MCP Server ready to accept connections")
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
    except Exception as e:
        logger.error("Fatal error in server", error=str(e))
        sys.exit(1)
    finally:
        logger.info("MCP Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())