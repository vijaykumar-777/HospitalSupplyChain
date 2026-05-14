# Project: Hospital Supply Chain — Delivery Delay & Disaster Prediction System

## What This Is
A system for hospitals that predicts delivery delays per order and suggests alternate suppliers. It includes a disaster mode that monitors real-time disaster alerts, predicts demand surges, identifies blocked routes, and recommends emergency suppliers.

## Core Value
To ensure hospitals never run out of life-critical supplies during normal operations and disasters by using AI for predictive delay management and dynamic emergency sourcing.

## Context
- **Tech Stack**: React 18, FastAPI, SQLite (dev)/PostgreSQL (prod), SQLAlchemy, Ollama (Qwen2.5/Llama3 local LLM), Leaflet maps.
- **Constraints**: Fully synthetic data generation using Python/Faker. No cloud AI costs (runs locally via Ollama).
- **External Services**: GDACS, ReliefWeb API, NewsAPI, OpenRouteService, Nominatim.

## Key Decisions
| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use local LLM (Ollama) | Eliminate cloud AI costs and ensure privacy | — Pending |
| fully synthetic data | Project doesn't have real hospital data, must be statistically realistic | — Pending |
| dual-mode dashboard | Clear visual separation between normal operations and disaster situations | — Pending |

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] [REQ-GEN-01] Generate realistic synthetic data for 11 schema tables
- [ ] [REQ-API-01] Build FastAPI backend for orders, POs, GRNs, suppliers, inventory
- [ ] [REQ-AI-01] Implement Ollama integration for predictive delay
- [ ] [REQ-AI-02] Implement Ollama integration for disaster analysis
- [ ] [REQ-EXT-01] Integrate external disaster & routing APIs
- [ ] [REQ-UI-01] Build React frontend with dual-mode dashboard
- [ ] [REQ-SIM-01] Implement live simulation layer for demos

### Out of Scope

- Real-world production medical data — Using synthetic data
- Cloud AI APIs (OpenAI/Anthropic) — Using local Ollama to save costs

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-14 after initialization*
