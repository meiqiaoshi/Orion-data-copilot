# Design Decisions

---

## 1. Why Hybrid Planner (LLM + Rules)?

### Decision
Use an LLM-based planner with a rule-based fallback.

### Reasoning
- LLM provides flexibility in understanding diverse queries
- Rule-based planner ensures deterministic behavior and reliability
- Prevents system failure when LLM is unavailable

### Trade-off
- Slightly higher complexity vs pure rule-based system
- More maintainable than pure LLM-driven approach

---

## 2. Why Not Direct NL → SQL?

### Decision
Use structured plan (intent + filters) instead of direct SQL generation.

### Reasoning
- Safer and more controllable
- Easier to debug and extend
- Aligns with real-world data platform architectures

### Trade-off
- Requires additional abstraction layer
- Less flexible than full NL-to-SQL systems

---

## 3. Why Connector-Based Architecture?

### Decision
Separate data access into connectors.

### Reasoning
- Decouples data sources from logic
- Supports multi-source querying (IngestFlow + SentinelDQ)
- Easier to extend with new systems

---

## 4. Why Use SentinelDQ API Instead of Raw SQL?

### Decision
Reuse SentinelDQ's metadata store API (`get_recent_alerts`).

### Reasoning
- Avoids schema mismatch issues
- More stable than direct DB queries
- Closer to production integration patterns

---

## 5. Why CLI Instead of Web UI?

### Decision
Use CLI for MVP.

### Reasoning
- Faster to build
- Focus on core system logic
- UI can be added later

---

## 6. Why AI-style Formatter?

### Decision
Transform results into human-readable summaries.

### Reasoning
- Improves usability
- Mimics copilot-like experience
- Highlights important insights (not just raw data)

---

## Summary

The system prioritizes:
- reliability (fallbacks)
- modularity (connectors)
- clarity (structured plans)
- usability (formatted output)