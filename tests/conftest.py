"""
Configuración de pytest para el proyecto.
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Crea un bucle de eventos para toda la sesión de tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()