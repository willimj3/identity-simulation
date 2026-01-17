# Group Identity Simulation Platform

A research-grade web application for simulating how political messages propagate through different worldviews, grounded in social psychology research.

## Features

- **Message Analysis**: Test how political messages are received by different audiences
- **Five Personas**: Conservative, Libertarian, Moderate, Liberal, and Progressive (based on Moral Foundations Theory)
- **Detailed Psychological Breakdown**: Receptivity scores, moral foundations analysis, concerns, resonance points, barriers to persuasion
- **Context Types**: Analyze messages as social media posts, policy briefs, speeches, news articles, or campaign ads
- **Comparison View**: Side-by-side analysis with visual charts
- **History Tracking**: Save and revisit past simulations
- **Export**: Download results as CSV or PDF
- **File Upload**: Upload documents (PDF, DOCX, TXT) for analysis

## Research Grounding

Personas are based on peer-reviewed research:
- Jonathan Haidt's Moral Foundations Theory
- Dan Kahan's Cultural Cognition framework
- Campbell & Kay (2014) on solution aversion
- Gromet et al. (2013) on political ideology and environmental behavior

## The Personas

| Persona | Moral Foundations | Cultural Cognition |
|---------|-------------------|-------------------|
| **Conservative** | High on Authority, Loyalty, Sanctity | Hierarchical-Individualist |
| **Libertarian** | Very high on Liberty | Strong Individualist |
| **Moderate** | Balanced across all dimensions | Center on both axes |
| **Liberal** | High on Care, Fairness (equality) | Egalitarian-Communitarian |
| **Progressive** | High on Care (systemic), Fairness (structural) | Strongly Egalitarian |

## Tech Stack

- **Backend**: FastAPI (Python) + SQLite
- **Frontend**: React + Vite
- **AI**: Anthropic Claude API
- **Charts**: Recharts

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Build for Production
```bash
cd frontend
npm run build  # Outputs to backend/static
```

## Deployment

This app is configured for Railway deployment:

1. Connect your GitHub repository to Railway
2. Set the environment variable: `ANTHROPIC_API_KEY=your-api-key`
3. Railway will auto-detect and deploy

## Environment Variables

- `ANTHROPIC_API_KEY` (required): Your Anthropic API key for Claude
- `PORT` (optional): Port to run the server (default: 8000)

## API Endpoints

- `POST /api/simulate` - Run a simulation
- `GET /api/simulations` - List past simulations
- `GET /api/simulations/{id}` - Get simulation details
- `DELETE /api/simulations/{id}` - Delete a simulation
- `GET /api/simulations/{id}/export?format=csv|pdf` - Export results
- `GET /api/personas` - List available personas
- `POST /api/upload` - Upload a document for text extraction
- `GET /api/health` - Health check
