"""
Tests de integración para el servidor MCP.
"""

import pytest
import asyncio

from src.tools.registry import ToolRegistry
from src.tools.basic_tools import register_basic_tools


class TestMCPIntegration:
    """Tests de integración del servidor MCP."""
    
    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test registro de herramientas."""
        registry = ToolRegistry()
        await register_basic_tools(registry)
        
        assert registry.get_tools_count() > 0
        assert "calculator" in registry.get_tool_names()
        assert "echo" in registry.get_tool_names()
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test ejecución de herramientas."""
        registry = ToolRegistry()
        await register_basic_tools(registry)
        
        # Test calculadora
        result = await registry.execute_tool("calculator", {
            "operation": "add",
            "a": 5,
            "b": 3
        })
        
        assert len(result) > 0
        assert "8" in str(result[0])
    
    @pytest.mark.asyncio
    async def test_tool_listing(self):
        """Test listado de herramientas."""
        registry = ToolRegistry()
        await register_basic_tools(registry)
        
        tools = await registry.list_tools()
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        assert "calculator" in tool_names
        assert "text_processor" in tool_names