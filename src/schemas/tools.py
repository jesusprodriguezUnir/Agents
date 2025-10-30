"""
Esquemas de herramientas para el sistema MCP.

Define las estructuras de respuesta y validación para las herramientas MCP.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Resultado de la ejecución de una herramienta MCP."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de respuesta")
    error_code: Optional[str] = Field(None, description="Código de error específico")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")


class ToolError(BaseModel):
    """Error en la ejecución de una herramienta MCP."""
    
    code: str = Field(..., description="Código del error")
    message: str = Field(..., description="Mensaje del error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")


class ToolSchema(BaseModel):
    """Esquema de definición de una herramienta MCP."""
    
    name: str = Field(..., description="Nombre de la herramienta")
    description: str = Field(..., description="Descripción de la herramienta")
    input_schema: Dict[str, Any] = Field(..., description="Esquema de entrada JSON Schema")
    output_schema: Dict[str, Any] = Field(..., description="Esquema de salida JSON Schema")
    examples: Optional[list] = Field(None, description="Ejemplos de uso")
    tags: Optional[list] = Field(None, description="Etiquetas de categorización")


class MCPToolDefinition(BaseModel):
    """Definición completa de una herramienta MCP para el protocolo."""
    
    name: str = Field(..., description="Nombre único de la herramienta")
    description: str = Field(..., description="Descripción de qué hace la herramienta")
    inputSchema: Dict[str, Any] = Field(..., description="JSON Schema para validar entrada")
    
    class Config:
        # Permitir nombres de campo en camelCase para compatibilidad MCP
        allow_population_by_field_name = True


class MCPResource(BaseModel):
    """Definición de un recurso MCP."""
    
    uri: str = Field(..., description="URI único del recurso")
    name: str = Field(..., description="Nombre del recurso")
    description: str = Field(..., description="Descripción del recurso")
    mimeType: str = Field(..., description="Tipo MIME del recurso")
    
    class Config:
        allow_population_by_field_name = True


class MCPPrompt(BaseModel):
    """Definición de un prompt MCP."""
    
    name: str = Field(..., description="Nombre único del prompt")
    description: str = Field(..., description="Descripción del prompt")
    arguments: Optional[list] = Field(None, description="Argumentos del prompt")
    
    class Config:
        allow_population_by_field_name = True