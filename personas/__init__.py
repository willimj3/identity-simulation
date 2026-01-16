"""
Persona module for the Group Identity Simulation Platform.
Each persona is a carefully crafted system prompt grounded in social psychology research.
"""

from .conservative import CONSERVATIVE_PERSONA
from .libertarian import LIBERTARIAN_PERSONA
from .moderate import MODERATE_PERSONA
from .liberal import LIBERAL_PERSONA
from .progressive import PROGRESSIVE_PERSONA

PERSONAS = {
    "conservative": CONSERVATIVE_PERSONA,
    "libertarian": LIBERTARIAN_PERSONA,
    "moderate": MODERATE_PERSONA,
    "liberal": LIBERAL_PERSONA,
    "progressive": PROGRESSIVE_PERSONA,
}

__all__ = [
    "PERSONAS",
    "CONSERVATIVE_PERSONA",
    "LIBERTARIAN_PERSONA",
    "MODERATE_PERSONA",
    "LIBERAL_PERSONA",
    "PROGRESSIVE_PERSONA",
]
