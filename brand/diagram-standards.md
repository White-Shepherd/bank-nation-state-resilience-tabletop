# Diagram Standards

Diagrams must be understandable without narration and must show declared causality only.

- Critical-service chain: need -> service -> process -> application/data -> control plane -> recovery.
- Tier 0 concentration: services above shared authority or recovery dependencies; counts are explicit relationship counts.
- Common-mode failure: shared dependency centered between affected services and compensating controls.
- Incident escalation: observed signal -> detecting capability -> receiving team -> accountable decision owner.
- Recovery sequence: clean authority -> independent infrastructure -> trusted data -> validation -> minimum viable service.
- Responsibility model: decision, responsible executor, accountable owner, alternate and deadline.
- Current versus target: mirror the same architecture categories and highlight removed common modes.
- Traceability chain: claim -> node/relationship identifier -> evidence -> decision.

Use native PowerPoint shapes for simple diagrams, build connectors before nodes, label every arrow, and avoid crossed lines. Complex topology may use Graphviz only when progressive disclosure cannot keep native diagrams readable.
