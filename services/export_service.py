"""
Export service for generating CSV and PDF reports of simulation results.
"""

import csv
import io
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak


def generate_csv(simulation: dict) -> str:
    """
    Generate CSV export of simulation results.

    Args:
        simulation: Simulation dict with responses

    Returns:
        CSV string
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Persona",
        "Receptivity Score",
        "Initial Reaction",
        "Emotional Response",
        "Concerns",
        "What Resonates",
        "Barriers to Persuasion",
        "Trust Factors",
        "Suggested Reframings",
        "Identity Protective Reasoning",
        "Authentic Voice Response"
    ])

    # Data rows
    for response in simulation.get("responses", []):
        # Handle JSON fields that might be stored as strings or lists
        concerns = response.get("concerns", [])
        if isinstance(concerns, str):
            try:
                concerns = json.loads(concerns)
            except:
                concerns = [concerns]

        resonates = response.get("what_resonates", [])
        if isinstance(resonates, str):
            try:
                resonates = json.loads(resonates)
            except:
                resonates = [resonates]

        barriers = response.get("barriers", [])
        if isinstance(barriers, str):
            try:
                barriers = json.loads(barriers)
            except:
                barriers = [barriers]

        reframings = response.get("suggested_reframings", [])
        if isinstance(reframings, str):
            try:
                reframings = json.loads(reframings)
            except:
                reframings = [reframings]

        writer.writerow([
            response.get("persona_name", ""),
            response.get("receptivity_score", ""),
            response.get("initial_reaction", ""),
            response.get("emotional_response", ""),
            "; ".join(concerns) if isinstance(concerns, list) else concerns,
            "; ".join(resonates) if isinstance(resonates, list) else resonates,
            "; ".join(barriers) if isinstance(barriers, list) else barriers,
            response.get("trust_factors", ""),
            "; ".join(reframings) if isinstance(reframings, list) else reframings,
            response.get("identity_protective_reasoning", ""),
            response.get("authentic_voice_response", "")
        ])

    return output.getvalue()


def generate_pdf(simulation: dict) -> bytes:
    """
    Generate PDF report of simulation results.

    Args:
        simulation: Simulation dict with responses

    Returns:
        PDF bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#1a365d')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2d3748')
    )

    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#4a5568')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=6,
        spaceAfter=6,
        textColor=colors.HexColor('#2d3748')
    )

    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=10,
        spaceAfter=10,
        textColor=colors.HexColor('#4a5568'),
        backColor=colors.HexColor('#f7fafc'),
        borderPadding=10
    )

    story = []

    # Title
    story.append(Paragraph("Group Identity Simulation Report", title_style))
    story.append(Spacer(1, 12))

    # Metadata
    created_at = simulation.get("created_at", datetime.now().isoformat())
    if isinstance(created_at, str):
        created_at = created_at[:19]  # Truncate to remove microseconds

    story.append(Paragraph(f"<b>Date:</b> {created_at}", body_style))
    story.append(Paragraph(f"<b>Context Type:</b> {simulation.get('context_type', 'general').replace('_', ' ').title()}", body_style))
    story.append(Spacer(1, 12))

    # Message
    story.append(Paragraph("Message Analyzed", heading_style))
    message = simulation.get("message", "").replace("\n", "<br/>")
    story.append(Paragraph(f'"{message}"', quote_style))
    story.append(Spacer(1, 20))

    # Summary table
    story.append(Paragraph("Receptivity Summary", heading_style))

    table_data = [["Persona", "Receptivity Score", "Initial Reaction"]]
    for response in simulation.get("responses", []):
        score = response.get("receptivity_score", "N/A")
        initial = response.get("initial_reaction", "")[:80] + "..." if len(response.get("initial_reaction", "")) > 80 else response.get("initial_reaction", "")
        table_data.append([
            response.get("persona_name", "").title(),
            str(score),
            initial
        ])

    if len(table_data) > 1:
        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(table)

    story.append(PageBreak())

    # Detailed responses
    for response in simulation.get("responses", []):
        persona_name = response.get("persona_name", "Unknown").title()
        story.append(Paragraph(f"{persona_name} Response", heading_style))

        # Score
        score = response.get("receptivity_score", "N/A")
        story.append(Paragraph(f"<b>Receptivity Score:</b> {score}/100", body_style))

        # Initial reaction
        story.append(Paragraph("<b>Initial Reaction:</b>", body_style))
        story.append(Paragraph(response.get("initial_reaction", "N/A"), quote_style))

        # Emotional response
        story.append(Paragraph("<b>Emotional Response:</b>", body_style))
        story.append(Paragraph(response.get("emotional_response", "N/A"), body_style))

        # Concerns
        concerns = response.get("concerns", [])
        if isinstance(concerns, str):
            try:
                concerns = json.loads(concerns)
            except:
                concerns = [concerns]
        if concerns:
            story.append(Paragraph("<b>Concerns:</b>", body_style))
            for concern in concerns:
                story.append(Paragraph(f"• {concern}", body_style))

        # What resonates
        resonates = response.get("what_resonates", [])
        if isinstance(resonates, str):
            try:
                resonates = json.loads(resonates)
            except:
                resonates = [resonates]
        if resonates:
            story.append(Paragraph("<b>What Resonates:</b>", body_style))
            for item in resonates:
                story.append(Paragraph(f"• {item}", body_style))

        # Barriers
        barriers = response.get("barriers", [])
        if isinstance(barriers, str):
            try:
                barriers = json.loads(barriers)
            except:
                barriers = [barriers]
        if barriers:
            story.append(Paragraph("<b>Barriers to Persuasion:</b>", body_style))
            for barrier in barriers:
                story.append(Paragraph(f"• {barrier}", body_style))

        # Suggested reframings
        reframings = response.get("suggested_reframings", [])
        if isinstance(reframings, str):
            try:
                reframings = json.loads(reframings)
            except:
                reframings = [reframings]
        if reframings:
            story.append(Paragraph("<b>Suggested Reframings:</b>", body_style))
            for reframing in reframings:
                story.append(Paragraph(f"• {reframing}", body_style))

        # Authentic voice
        story.append(Paragraph("<b>Authentic Voice Response:</b>", body_style))
        authentic = response.get("authentic_voice_response", "N/A")
        story.append(Paragraph(authentic, quote_style))

        story.append(PageBreak())

    # Build PDF
    doc.build(story)
    return buffer.getvalue()
