"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MoralFoundationsAnalysis(BaseModel):
    """Analysis across the six moral foundations."""
    care_harm: str = Field(description="How care/harm foundation is triggered")
    fairness_cheating: str = Field(description="How fairness/cheating foundation is triggered")
    loyalty_betrayal: str = Field(description="How loyalty/betrayal foundation is triggered")
    authority_subversion: str = Field(description="How authority/subversion foundation is triggered")
    sanctity_degradation: str = Field(description="How sanctity/degradation foundation is triggered")
    liberty_oppression: str = Field(description="How liberty/oppression foundation is triggered")


class PersonaResponse(BaseModel):
    """Structured response from a persona analysis."""
    receptivity_score: int = Field(ge=0, le=100, description="0-100 receptivity score")
    initial_reaction: str = Field(description="Gut-level first impression")
    emotional_response: str = Field(description="Emotional feelings evoked")
    moral_foundations_analysis: MoralFoundationsAnalysis
    concerns: list[str] = Field(description="Specific objections or concerns")
    what_resonates: list[str] = Field(description="What works positively")
    barriers_to_persuasion: list[str] = Field(description="Why persuasion fails")
    trust_factors: str = Field(description="Source credibility assessment")
    suggested_reframings: list[str] = Field(description="How to improve the message")
    identity_protective_reasoning: str = Field(description="How identity shapes interpretation")
    authentic_voice_response: str = Field(description="200-word response in persona's voice")


class SimulationRequest(BaseModel):
    """Request to simulate message reception."""
    message: str = Field(min_length=1, description="The message to analyze")
    context_type: str = Field(default="general", description="Context type: tweet, policy_brief, speech, etc.")
    personas: list[str] = Field(default=["conservative", "libertarian", "moderate"],
                                 description="Which personas to simulate")


class PersonaResponseWithMeta(BaseModel):
    """Persona response with metadata."""
    persona_name: str
    response: PersonaResponse


class SimulationResponse(BaseModel):
    """Full simulation response."""
    simulation_id: int
    message: str
    context_type: str
    created_at: datetime
    responses: list[PersonaResponseWithMeta]


class SimulationSummary(BaseModel):
    """Summary of a simulation for listing."""
    id: int
    message: str
    context_type: str
    created_at: datetime
    response_count: int
    avg_receptivity: Optional[float]


class PersonaInfo(BaseModel):
    """Information about an available persona."""
    name: str
    display_name: str
    description: str
    moral_foundations_profile: dict[str, str]
    cultural_cognition: str
    key_triggers: list[str]
    key_bridges: list[str]


class ExportRequest(BaseModel):
    """Request for export."""
    format: str = Field(default="csv", description="Export format: csv or pdf")
