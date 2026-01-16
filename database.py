"""
Database module for the Group Identity Simulation Platform.
Uses SQLite with aiosqlite for async operations.
"""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

DATABASE_PATH = Path(__file__).parent / "simulations.db"


async def get_db():
    """Get database connection."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database with schema."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                context_type TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS persona_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER NOT NULL,
                persona_name TEXT NOT NULL,
                receptivity_score INTEGER,
                initial_reaction TEXT,
                emotional_response TEXT,
                moral_foundations_analysis TEXT,
                concerns TEXT,
                what_resonates TEXT,
                barriers TEXT,
                trust_factors TEXT,
                suggested_reframings TEXT,
                identity_protective_reasoning TEXT,
                authentic_voice_response TEXT,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_persona_responses_simulation
            ON persona_responses(simulation_id);
        """)
        await db.commit()


async def create_simulation(message: str, context_type: str = "general") -> int:
    """Create a new simulation record and return its ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO simulations (message, context_type) VALUES (?, ?)",
            (message, context_type)
        )
        await db.commit()
        return cursor.lastrowid


async def save_persona_response(
    simulation_id: int,
    persona_name: str,
    response_data: dict
) -> int:
    """Save a persona response to the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO persona_responses (
                simulation_id, persona_name, receptivity_score, initial_reaction,
                emotional_response, moral_foundations_analysis, concerns,
                what_resonates, barriers, trust_factors, suggested_reframings,
                identity_protective_reasoning, authentic_voice_response, raw_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                simulation_id,
                persona_name,
                response_data.get("receptivity_score"),
                response_data.get("initial_reaction"),
                response_data.get("emotional_response"),
                json.dumps(response_data.get("moral_foundations_analysis", {})),
                json.dumps(response_data.get("concerns", [])),
                json.dumps(response_data.get("what_resonates", [])),
                json.dumps(response_data.get("barriers_to_persuasion", [])),
                response_data.get("trust_factors"),
                json.dumps(response_data.get("suggested_reframings", [])),
                response_data.get("identity_protective_reasoning"),
                response_data.get("authentic_voice_response"),
                json.dumps(response_data)
            )
        )
        await db.commit()
        return cursor.lastrowid


async def get_simulation(simulation_id: int) -> Optional[dict]:
    """Get a simulation with all its persona responses."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get simulation
        cursor = await db.execute(
            "SELECT * FROM simulations WHERE id = ?",
            (simulation_id,)
        )
        sim_row = await cursor.fetchone()
        if not sim_row:
            return None

        simulation = dict(sim_row)

        # Get persona responses
        cursor = await db.execute(
            "SELECT * FROM persona_responses WHERE simulation_id = ? ORDER BY persona_name",
            (simulation_id,)
        )
        rows = await cursor.fetchall()

        responses = []
        for row in rows:
            response = dict(row)
            # Parse JSON fields
            for field in ["moral_foundations_analysis", "concerns", "what_resonates",
                         "barriers", "suggested_reframings", "raw_response"]:
                if response.get(field):
                    try:
                        response[field] = json.loads(response[field])
                    except json.JSONDecodeError:
                        pass
            responses.append(response)

        simulation["responses"] = responses
        return simulation


async def get_all_simulations(limit: int = 50, offset: int = 0) -> list:
    """Get all simulations with summary info."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """SELECT s.*,
                      COUNT(pr.id) as response_count,
                      AVG(pr.receptivity_score) as avg_receptivity
               FROM simulations s
               LEFT JOIN persona_responses pr ON s.id = pr.simulation_id
               GROUP BY s.id
               ORDER BY s.created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_simulation(simulation_id: int) -> bool:
    """Delete a simulation and its responses."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Delete responses first (foreign key)
        await db.execute(
            "DELETE FROM persona_responses WHERE simulation_id = ?",
            (simulation_id,)
        )
        cursor = await db.execute(
            "DELETE FROM simulations WHERE id = ?",
            (simulation_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
