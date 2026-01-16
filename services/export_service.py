"""
Export service for generating CSV and PDF reports of simulation results.
"""

import csv
import io
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# Warm color palette matching the UI
COLORS = {
    'text': colors.HexColor('#1a1a1a'),
    'text_secondary': colors.HexColor('#5c5c5c'),
    'text_muted': colors.HexColor('#8c8c8c'),
    'bg': colors.HexColor('#f9f8f6'),
    'border': colors.HexColor('#e8e5e0'),
    'accent': colors.HexColor('#c9b896'),
    'success': colors.HexColor('#5a7a64'),
    'warning': colors.HexColor('#b8956c'),
    'danger': colors.HexColor('#a65d5d'),
    'conservative': colors.HexColor('#a65d5d'),
    'libertarian': colors.HexColor('#b8956c'),
    'moderate': colors.HexColor('#7d6b99'),
}


def generate_csv(simulation: dict) -> str:
    """
    Generate CSV export of simulation results.
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
        concerns = _parse_json_field(response.get("concerns", []))
        resonates = _parse_json_field(response.get("what_resonates", []))
        barriers = _parse_json_field(response.get("barriers", []))
        reframings = _parse_json_field(response.get("suggested_reframings", []))

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


def _parse_json_field(field):
    """Parse a field that might be JSON string or already a list."""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return [field] if field else []
    return field or []


def _get_score_color(score):
    """Get color based on score value."""
    if score < 40:
        return COLORS['danger']
    elif score < 70:
        return COLORS['warning']
    return COLORS['success']


def _get_score_label(score):
    """Get label based on score value."""
    if score < 40:
        return "Low Receptivity"
    elif score < 70:
        return "Mixed Reception"
    return "Positive Reception"


def _get_persona_color(persona_name):
    """Get color for persona."""
    name = persona_name.lower()
    return COLORS.get(name, COLORS['text_secondary'])


def _truncate(text, max_length=100):
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."


def generate_pdf(simulation: dict) -> bytes:
    """
    Generate PDF report of simulation results.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=60,
        leftMargin=60,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles - warm, minimal aesthetic
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Times-Roman',
        fontSize=28,
        spaceAfter=8,
        textColor=COLORS['text'],
        leading=34
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=30,
        textColor=COLORS['text_muted']
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Times-Roman',
        fontSize=18,
        spaceBefore=24,
        spaceAfter=12,
        textColor=COLORS['text'],
        leading=22
    )

    persona_title_style = ParagraphStyle(
        'PersonaTitle',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=14,
        spaceBefore=0,
        spaceAfter=4,
        textColor=COLORS['text']
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        spaceBefore=12,
        spaceAfter=4,
        textColor=COLORS['text_muted'],
        leading=11
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceBefore=2,
        spaceAfter=6,
        textColor=COLORS['text'],
        leading=14
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leftIndent=12,
        spaceBefore=2,
        spaceAfter=2,
        textColor=COLORS['text'],
        leading=14
    )

    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leftIndent=16,
        rightIndent=16,
        spaceBefore=8,
        spaceAfter=8,
        textColor=COLORS['text_secondary'],
        leading=15
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leftIndent=12,
        spaceBefore=4,
        spaceAfter=4,
        textColor=COLORS['text'],
        leading=14
    )

    story = []

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 60))
    story.append(Paragraph("Identity Simulation Report", title_style))

    created_at = simulation.get("created_at", datetime.now().isoformat())
    if isinstance(created_at, str):
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%B %d, %Y")
        except:
            date_str = created_at[:10]
    else:
        date_str = str(created_at)[:10]

    context_type = simulation.get('context_type', 'general').replace('_', ' ').title()
    story.append(Paragraph(f"{date_str}  ·  {context_type}", subtitle_style))

    # Brief message excerpt (not the full thing)
    message = simulation.get("message", "")
    message_excerpt = _truncate(message, 150)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS['border']))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Message Analyzed", label_style))
    story.append(Paragraph(f'"{message_excerpt}"', quote_style))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS['border']))

    # ===== EXECUTIVE SUMMARY =====
    story.append(Spacer(1, 30))
    story.append(Paragraph("Summary", section_title_style))

    responses = simulation.get("responses", [])

    # Score overview table
    if responses:
        table_data = []
        for response in responses:
            persona = response.get("persona_name", "Unknown").title()
            score = response.get("receptivity_score", 0)
            label = _get_score_label(score)
            table_data.append([persona, str(score), label])

        table = Table(table_data, colWidths=[1.8*inch, 0.8*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), COLORS['text']),
            ('TEXTCOLOR', (2, 0), (2, -1), COLORS['text_secondary']),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -2), 1, COLORS['border']),
        ]))

        # Color the score column based on value
        for i, response in enumerate(responses):
            score = response.get("receptivity_score", 0)
            score_color = _get_score_color(score)
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (1, i), (1, i), score_color),
            ]))

        story.append(table)

    # Key findings callout
    story.append(Spacer(1, 24))

    # Find common concerns and resonances across personas
    all_concerns = []
    all_resonates = []
    for response in responses:
        all_concerns.extend(_parse_json_field(response.get("concerns", [])))
        all_resonates.extend(_parse_json_field(response.get("what_resonates", [])))

    story.append(PageBreak())

    # ===== DETAILED PERSONA SECTIONS =====
    for i, response in enumerate(responses):
        persona_name = response.get("persona_name", "Unknown").title()
        score = response.get("receptivity_score", 0)
        persona_color = _get_persona_color(persona_name)

        # Persona header with colored bar
        header_table = Table(
            [[Paragraph(persona_name, persona_title_style),
              Paragraph(f"{score}/100", ParagraphStyle('Score', fontSize=14, fontName='Helvetica-Bold', textColor=_get_score_color(score)))]],
            colWidths=[4*inch, 1.5*inch]
        )
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, 0), 3, persona_color),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 12))

        # Initial reaction
        initial = response.get("initial_reaction", "")
        if initial:
            story.append(Paragraph(initial, body_style))
            story.append(Spacer(1, 8))

        # Two-column layout for What Resonates and Concerns
        resonates = _parse_json_field(response.get("what_resonates", []))
        concerns = _parse_json_field(response.get("concerns", []))

        if resonates or concerns:
            # Build content for each column
            resonates_content = []
            if resonates:
                resonates_content.append(Paragraph("WHAT RESONATES", ParagraphStyle('BoxLabel', fontSize=8, fontName='Helvetica-Bold', textColor=COLORS['success'], spaceAfter=6)))
                for item in resonates[:3]:  # Limit to 3
                    resonates_content.append(Paragraph(f"· {item}", callout_style))

            concerns_content = []
            if concerns:
                concerns_content.append(Paragraph("CONCERNS", ParagraphStyle('BoxLabel', fontSize=8, fontName='Helvetica-Bold', textColor=COLORS['warning'], spaceAfter=6)))
                for item in concerns[:3]:  # Limit to 3
                    concerns_content.append(Paragraph(f"· {item}", callout_style))

            # Create side-by-side boxes
            if resonates_content and concerns_content:
                box_table = Table(
                    [[resonates_content, concerns_content]],
                    colWidths=[3.2*inch, 3.2*inch]
                )
                box_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f0f7f2')),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#fdf8f3')),
                    ('LINEBELOW', (0, 0), (0, 0), 0, colors.white),
                    ('LINEBELOW', (1, 0), (1, 0), 0, colors.white),
                ]))
                story.append(box_table)
                story.append(Spacer(1, 12))

        # Barriers
        barriers = _parse_json_field(response.get("barriers", []))
        if barriers:
            story.append(Paragraph("BARRIERS TO PERSUASION", label_style))
            for barrier in barriers[:3]:
                story.append(Paragraph(f"· {barrier}", bullet_style))
            story.append(Spacer(1, 8))

        # Suggested Reframings - important section
        reframings = _parse_json_field(response.get("suggested_reframings", []))
        if reframings:
            story.append(Paragraph("SUGGESTED REFRAMINGS", label_style))
            for reframing in reframings[:3]:
                story.append(Paragraph(f"→ {reframing}", bullet_style))
            story.append(Spacer(1, 8))

        # Authentic voice (condensed)
        authentic = response.get("authentic_voice_response", "")
        if authentic:
            story.append(Paragraph("IN THEIR OWN WORDS", label_style))
            story.append(Paragraph(f'"{_truncate(authentic, 300)}"', quote_style))

        # Add page break between personas (except last one)
        if i < len(responses) - 1:
            story.append(PageBreak())

    # Build PDF
    doc.build(story)
    return buffer.getvalue()
