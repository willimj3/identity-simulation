# Group Identity Simulation Platform

A research-grade web application for simulating how political messages propagate through different worldviews, grounded in social psychology research.

## Features

- **Message Analysis**: Test how political/climate messages are received by different audiences
- **Three Personas**: Conservative, Libertarian, and Moderate (based on Moral Foundations Theory)
- **Detailed Psychological Breakdown**: Receptivity scores, concerns, resonance points, barriers
- **Comparison View**: Side-by-side analysis with visual charts
- **History Tracking**: Save and revisit past simulations
- **Export**: Download results as CSV or PDF

## Research Grounding

Personas are based on peer-reviewed research:
- Jonathan Haidt's Moral Foundations Theory
- Dan Kahan's Cultural Cognition framework
- Campbell & Kay (2014) on solution aversion
- Gromet et al. (2013) on political ideology and environmental behavior

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
- `GET /api/health` - Health check
