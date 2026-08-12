# Architecture

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK**

Streamlit provides the exercise controller and board interface. Pydantic validates YAML models. The deterministic engine evaluates explicit Tier 0 rules, shared dependencies, impact consumption, and transitions. Reporting generates Markdown and PDF. Session state holds exercise decisions; production use would require authenticated, encrypted, auditable persistence and retention controls. Data flows from labeled YAML to models to views and reports; no external service, secret, AI judgment, or real-bank data is required.

