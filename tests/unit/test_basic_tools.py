"""
Tests para el módulo de herramientas básicas.
"""

import pytest
import asyncio

from src.tools.basic_tools import (
    calculator_tool,
    text_tool,
    system_info_tool,
    echo_tool
)


class TestCalculatorTool:
    """Tests para la herramienta calculadora."""
    
    @pytest.mark.asyncio
    async def test_addition(self):
        """Test suma básica."""
        result = await calculator_tool("add", 5, 3)
        assert "8" in result
    
    @pytest.mark.asyncio
    async def test_division_by_zero(self):
        """Test división por cero."""
        result = await calculator_tool("divide", 5, 0)
        assert "Error" in result
    
    @pytest.mark.asyncio
    async def test_square_root(self):
        """Test raíz cuadrada."""
        result = await calculator_tool("sqrt", 9)
        assert "3" in result


class TestTextTool:
    """Tests para la herramienta de texto."""
    
    @pytest.mark.asyncio
    async def test_uppercase(self):
        """Test conversión a mayúsculas."""
        result = await text_tool("upper", "hello")
        assert result == "HELLO"
    
    @pytest.mark.asyncio
    async def test_reverse(self):
        """Test inversión de texto."""
        result = await text_tool("reverse", "hello")
        assert result == "olleh"
    
    @pytest.mark.asyncio
    async def test_word_count(self):
        """Test conteo de palabras."""
        result = await text_tool("count", "hello world")
        assert "Palabras: 2" in result


class TestSystemInfoTool:
    """Tests para la herramienta de información del sistema."""
    
    @pytest.mark.asyncio
    async def test_system_info(self):
        """Test obtención de información del sistema."""
        result = await system_info_tool()
        assert "platform" in result.lower()
        assert "python_version" in result.lower()


class TestEchoTool:
    """Tests para la herramienta de eco."""
    
    @pytest.mark.asyncio
    async def test_echo(self):
        """Test función de eco."""
        message = "test message"
        result = await echo_tool(message)
        assert message in result