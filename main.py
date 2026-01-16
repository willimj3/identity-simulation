"""
FastAPI application for the Group Identity Simulation Platform.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io

from database import init_db, create_simulation, save_persona_response, get_simulation, get_all_simulations, delete_simulation
from schemas import SimulationRequest, SimulationResponse, SimulationSummary, PersonaInfo, PersonaResponseWithMeta, PersonaResponse, MoralFoundationsAnalysis
from personas import PERSONAS
from services.claude_service import generate_all_persona_responses
from services.export_service import generate_csv, generate_pdf

# Static files directory (built frontend)
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Group Identity Simulation Platform",
    description="Simulate how political messages are received across different worldviews",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend (allow all origins for production flexibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/personas", response_model=list[PersonaInfo])
async def list_personas():
    """Get list of available personas with their configurations."""
    personas_list = []
    for name, config in PERSONAS.items():
        personas_list.append(PersonaInfo(
            name=config["name"],
            display_name=config["display_name"],
            description=config["description"],
            moral_foundations_profile=config["moral_foundations_profile"],
            cultural_cognition=config["cultural_cognition"],
            key_triggers=config["key_triggers"],
            key_bridges=config["key_bridges"]
        ))
    return personas_list


@app.post("/api/simulate")
async def simulate_message(request: SimulationRequest):
    """
    Simulate how a message is received across selected personas.
    Returns structured analysis from each persona's perspective.
    """
    # Validate personas
    valid_personas = [p for p in request.personas if p in PERSONAS]
    if not valid_personas:
        raise HTTPException(status_code=400, detail="No valid personas selected")

    # Create simulation record
    simulation_id = await create_simulation(request.message, request.context_type)

    # Generate responses from all personas in parallel
    responses = await generate_all_persona_responses(
        PERSONAS,
        valid_personas,
        request.message,
        request.context_type
    )

    # Save responses and build response object
    response_list = []
    for persona_name, response_data in responses.items():
        await save_persona_response(simulation_id, persona_name, response_data)

        # Build typed response
        try:
            moral_analysis = MoralFoundationsAnalysis(
                care_harm=response_data.get("moral_foundations_analysis", {}).get("care_harm", ""),
                fairness_cheating=response_data.get("moral_foundations_analysis", {}).get("fairness_cheating", ""),
                loyalty_betrayal=response_data.get("moral_foundations_analysis", {}).get("loyalty_betrayal", ""),
                authority_subversion=response_data.get("moral_foundations_analysis", {}).get("authority_subversion", ""),
                sanctity_degradation=response_data.get("moral_foundations_analysis", {}).get("sanctity_degradation", ""),
                liberty_oppression=response_data.get("moral_foundations_analysis", {}).get("liberty_oppression", "")
            )

            persona_response = PersonaResponse(
                receptivity_score=response_data.get("receptivity_score", 50),
                initial_reaction=response_data.get("initial_reaction", ""),
                emotional_response=response_data.get("emotional_response", ""),
                moral_foundations_analysis=moral_analysis,
                concerns=response_data.get("concerns", []),
                what_resonates=response_data.get("what_resonates", []),
                barriers_to_persuasion=response_data.get("barriers_to_persuasion", []),
                trust_factors=response_data.get("trust_factors", ""),
                suggested_reframings=response_data.get("suggested_reframings", []),
                identity_protective_reasoning=response_data.get("identity_protective_reasoning", ""),
                authentic_voice_response=response_data.get("authentic_voice_response", "")
            )

            response_list.append(PersonaResponseWithMeta(
                persona_name=persona_name,
                response=persona_response
            ))
        except Exception as e:
            # If parsing fails, still include partial response
            response_list.append({
                "persona_name": persona_name,
                "response": response_data,
                "parse_error": str(e)
            })

    return {
        "simulation_id": simulation_id,
        "message": request.message,
        "context_type": request.context_type,
        "created_at": datetime.now().isoformat(),
        "responses": response_list
    }


@app.get("/api/simulations")
async def list_simulations(limit: int = 50, offset: int = 0):
    """Get list of past simulations with summary info."""
    simulations = await get_all_simulations(limit, offset)
    return simulations


@app.get("/api/simulations/{simulation_id}")
async def get_simulation_detail(simulation_id: int):
    """Get detailed simulation with all persona responses."""
    simulation = await get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation


@app.delete("/api/simulations/{simulation_id}")
async def delete_simulation_endpoint(simulation_id: int):
    """Delete a simulation and its responses."""
    success = await delete_simulation(simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"status": "deleted", "id": simulation_id}


@app.get("/api/simulations/{simulation_id}/export")
async def export_simulation(simulation_id: int, format: str = "csv"):
    """Export simulation results as CSV or PDF."""
    simulation = await get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if format.lower() == "csv":
        csv_content = generate_csv(simulation)
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=simulation_{simulation_id}.csv"}
        )
    elif format.lower() == "pdf":
        pdf_content = generate_pdf(simulation)
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=simulation_{simulation_id}.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'pdf'")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Serve static files (built React frontend) if the directory exists
if STATIC_DIR.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    # Catch-all route for SPA - must be last
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the React SPA for any non-API routes."""
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        # Serve index.html for all other routes (SPA routing)
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
