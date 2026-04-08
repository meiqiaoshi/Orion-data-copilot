# System Design

## High-Level Architecture
User → LLM → Query Planner → Data Sources → Response

## Core Components
- LLM Interface
- Query Planner
- Tool Layer
- Metadata Store
- Connectors

## Data Flow
User Query → Intent Parsing → SQL Generation → Execution → Response

## Design Decisions
- Use DuckDB for lightweight querying
- Modular architecture for extensibility
- Start with rule-based + LLM hybrid
