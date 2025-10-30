"""
Esquemas del protocolo MCP (Model Context Protocol).

Define los tipos de datos y validadores para la comunicación
entre cliente y servidor MCP.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """
    Modelo base para todas las solicitudes MCP.
    """
    id: str = Field(..., description="Identificador único de la solicitud")
    method: str = Field(..., description="Método MCP a ejecutar")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Parámetros de la solicitud")


class MCPResponse(BaseModel):
    """
    Modelo base para todas las respuestas MCP.
    """
    id: str = Field(..., description="Identificador de la solicitud correspondiente")
    result: Optional[Any] = Field(default=None, description="Resultado de la operación")
    error: Optional["MCPError"] = Field(default=None, description="Error si la operación falló")


class MCPError(BaseModel):
    """
    Modelo para errores MCP.
    """
    code: int = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Datos adicionales del error")


class ToolSchema(BaseModel):
    """
    Esquema para definir herramientas MCP.
    """
    name: str = Field(..., description="Nombre único de la herramienta")
    description: str = Field(..., description="Descripción de la funcionalidad")
    input_schema: Dict[str, Any] = Field(..., description="Esquema JSON para validar entrada")
    
    class Config:
        """Configuración del modelo."""
        extra = "forbid"


class ToolExecutionRequest(BaseModel):
    """
    Solicitud para ejecutar una herramienta.
    """
    tool_name: str = Field(..., description="Nombre de la herramienta a ejecutar")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos para la herramienta")


class ToolExecutionResponse(BaseModel):
    """
    Respuesta de la ejecución de una herramienta.
    """
    success: bool = Field(..., description="Indica si la ejecución fue exitosa")
    result: Any = Field(default=None, description="Resultado de la ejecución")
    error_message: Optional[str] = Field(default=None, description="Mensaje de error si falló")
    execution_time: Optional[float] = Field(default=None, description="Tiempo de ejecución en segundos")


class ServerInfo(BaseModel):
    """
    Información del servidor MCP.
    """
    name: str = Field(..., description="Nombre del servidor")
    version: str = Field(..., description="Versión del servidor")
    protocol_version: str = Field(default="2024-11-05", description="Versión del protocolo MCP")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="Capacidades del servidor")


class ClientInfo(BaseModel):
    """
    Información del cliente MCP.
    """
    name: str = Field(..., description="Nombre del cliente")
    version: str = Field(..., description="Versión del cliente")


class InitializeRequest(BaseModel):
    """
    Solicitud de inicialización MCP.
    """
    protocol_version: str = Field(..., description="Versión del protocolo")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="Capacidades del cliente")
    client_info: ClientInfo = Field(..., description="Información del cliente")


class InitializeResponse(BaseModel):
    """
    Respuesta de inicialización MCP.
    """
    protocol_version: str = Field(..., description="Versión del protocolo soportada")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="Capacidades del servidor")
    server_info: ServerInfo = Field(..., description="Información del servidor")


# Códigos de error estándar MCP
class MCPErrorCodes:
    """Códigos de error estándar del protocolo MCP."""
    
    # Errores de protocolo
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Errores específicos de MCP
    TOOL_NOT_FOUND = -32000
    TOOL_EXECUTION_FAILED = -32001
    RESOURCE_NOT_FOUND = -32002
    UNAUTHORIZED = -32003