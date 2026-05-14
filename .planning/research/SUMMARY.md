# Research Summary

## Executive Summary
This project manages hospital supply chains by addressing normal delivery delays and disaster scenarios. It uses an AI-first approach with fully synthetic, statistically robust data. 

## Stack Recommendations
- **Frontend**: React 18, Vite, Tailwind CSS, Leaflet.js
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic, httpx
- **Database**: SQLite (dev) -> PostgreSQL (prod)
- **AI**: Ollama (Qwen2.5/Llama3 locally)
- **Background Tasks**: APScheduler

## Feature Categorization
- **Table Stakes**: Delivery delay tracking, order/inventory management
- **Differentiators**: Real-time disaster API integration (GDACS/ReliefWeb/NewsAPI), local AI reasoning for demand surges and ETA recalculations, Alternate routes calculation with OpenRouteService.
- **Anti-features**: Real-world cloud AI hosting (OpenAI), genuine medical data.

## Architecture Guidelines
- **Components**: Frontend Dashboard <-> FastAPI Backend <-> Ollama/SQLite
- **Data Flow**: Orders/Events trigger asynchronous AI evaluation; background pollers routinely update disaster state.
- **Dependencies**: Data generation must run before backend startup; database must be seeded before AI can evaluate history.

## Pitfalls to Avoid
- **Pitfall**: Brittle JSON parsing from LLMs. 
  - **Prevention**: Use robust regex to strip markdown blocks before loading JSON.
- **Pitfall**: Polling limits from external APIs.
  - **Prevention**: Cap polling intervals (e.g. 15 minutes) and cache results.
