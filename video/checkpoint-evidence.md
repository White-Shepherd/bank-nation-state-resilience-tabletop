# Checkpoint evidence register

| Checkpoint | Screenshot | Expected application state | Narration objective | Claim demonstrated | Supporting repository file | Limitation | Reset instruction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Overview | `screenshots/01-overview.png` | Read-only banner; four computed counts | Frame the end-to-end workflow | Service-led analysis connects to decisions | `src/harbor_resilience/demo.py` | Counts are synthetic, not risk scores | Reset Demo Mode |
| Critical service | `screenshots/02-critical-service.png` | Wire transfers and accountable owners | Start with business purpose | Service is distinct from its systems | Synthetic assessment JSON | Fictional service | Select Overview or reset |
| Impact tolerance | `screenshots/03-impact-tolerance.png` | MTD, RTO, RPO, workaround shown separately | Explain tolerable disruption | Targets retain distinct meanings | `assessment_models.py` | Target is not tested recovery | Select Overview or reset |
| Dependency map | `screenshots/04-dependency-map.png` | Deterministic declared graph | Trace service dependencies | Explicit dependencies support analysis | Ecosystem YAML | Undeclared links are not inferred | Select Overview or reset |
| Tier 0 | `screenshots/05-tier-0.png` | Rule output and pending decision | Explain candidate logic | Classification remains human-approved | `assessment.py` | Candidate is not final | Select Overview or reset |
| Concentration finding | `screenshots/06-concentration-finding.png` | Evidence-linked concentration rows | Connect common mode to action | Supported finding retains evidence | `assessment.py` | No likelihood or loss estimate | Select Overview or reset |
| Scenario warning | `screenshots/07-scenario-warning.png` | Phase 2 warning states and deadlines | Show ambiguity | Weak signals prompt review, not attribution | `scenario_states.yaml` | Fictional signal | Select Overview or reset |
| Integrity dilemma | `screenshots/08-integrity-dilemma.png` | Phase 5 dilemma and session decision | Explain containment tradeoff | Decision is recorded without source mutation | `demo.py` | Session record is not durable | Reset clears selection |
| Recovery | `screenshots/09-recovery.png` | Phase 6 prerequisites and selected decision | Validate trusted recovery path | Identity and data prerequisites precede service | `scenario_states.yaml` | Not proof of production recovery | Reset Demo Mode |
| Board packet | `screenshots/10-board-packet.png` | Findings, gaps, actions, packet preview | Translate evidence to governance | Output preserves uncertainty | `assessment.py` | Not a regulatory conclusion | Reset Demo Mode |
