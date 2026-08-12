# Agent Lesson Record

## Metadata

- Agent role: Lead information designer, banking-resilience architect, and presentation engineer
- Task: Evaluate and record evidence-backed builder lessons from the Harbor Ridge visual, presentation, and synthetic-data system
- Branch: `agent/add-product-demo-video-system`
- Commit reviewed or produced: `61a90f4a09051249d909120339f7f7183a65354b` (working branch); presentation system introduced by `2b512971646ea15c952764dc57c7be03bcbce371`; local `origin/main` inspected at `3be88292b0fb551339995f51cf4faca0f26a0e87`
- Date: 2026-08-12
- Status: proposed

## Objective

Record what the rendered Harbor Ridge artifacts and repository validation support about executive diagram selection, layout reliability, collision control, data traceability, accessibility, PowerPoint generation, and remaining design risk. This is a review record, not evidence that every requested artifact has been accepted by a banking subject-matter reviewer.

## Evidence Inspected

- User task brief: `C:\Users\baile\.codex\attachments\0a1b6717-594e-4a8c-ad56-524cc0e184c7\pasted-text.txt`.
- Protocol discovery: `docs/agent-learning/README.md`, decision records, unresolved-question records, and prior lessons were searched in the working tree and all locally tracked commits; none existed before this record.
- Presentation source: `scripts/generate_executive_presentation.mjs`; `src/harbor_resilience/presentation.py`; `scripts/generate_ecosystem_exports.py`.
- Design rules: `brand/brand-tokens.json`; `brand/visual-standards.md`; `brand/diagram-standards.md`; `brand/chart-standards.md`; `docs/executive-presentation-guide.md`.
- Editable deliverables: `presentations/board/executive-resilience-briefing.pptx` (12 slides); `presentations/technical/resilience-architecture-briefing.pptx` (11 slides); `presentations/tabletop/nation-state-exercise-facilitator.pptx` (14 slides); `presentations/templates/resilience-platform-template.pptx` (21 layouts).
- Rendered inspection: all slides on the executive, technical, and tabletop PNG contact sheets under `tmp/presentation-build/renders/`; full-size executive slides 4 and 6; full-size technical slide 8; legacy `docs/images/wire-transfer-service-map.png`; per-slide layout JSON and deck `inspect.ndjson` files.
- PDF/package evidence: board, technical, tabletop, brand-guide, and template-catalog PDFs checked by the repository suite.
- Synthetic records: `data/ecosystem/nodes.yaml` (126 nodes); `data/ecosystem/relationships.yaml` (108 relationships); `data/synthetic_assessments/harbor-ridge-2026.json`; presentation payload logic in `src/harbor_resilience/presentation.py`.
- Validation: `tests/test_assessment.py`, `tests/test_presentation.py`, `tests/test_brand_system.py`, and the complete test suite. Result: 64 passed in 3.01 seconds using the bundled workspace Python runtime.
- Version evidence: clean worktree before creation; current branch HEAD `61a90f4`; presentation commit `2b51297`; local `origin/main` `3be8829` does not contain the presentation system.

## Assumptions Tested

| Assumption | Test or evidence | Result |
|---|---|---|
| A single network view can communicate service, control-plane, third-party, and recovery relationships to executives. | Full-size inspection of `wire-transfer-service-map.png` showed long cross-canvas edges, intersecting paths, small labels, and weak grouping; curated deck views used subsets and explicit layers. | rejected |
| Deterministic layered and sequence views reduce visual ambiguity. | Executive slides 3, 6, 9, and 10 and technical slide 8 rendered with fixed coordinates, aligned nodes, and no observed connector/label collisions in the inspected PNGs. | confirmed |
| Passing deck tests proves presentation accessibility and visual correctness. | Tests verified package structure, notes, labels, and SVG title/description; inspection still found 13-point timeline labels and small chart labels below the declared 16-point body minimum. No automated contrast or collision test exists. | rejected |
| The identity concentration claim is traceable and is not a risk score. | `test_concentration_uses_declared_critical_relationships` recomputed seven critical inbound relationships for `IF-01`; slide 4 labels the metric as a relationship count and explicitly rejects probability/loss interpretation. | confirmed |
| Every high-level assessment record type is equally ready to support board claims. | The assessment JSON has broad normalized coverage, but only 12 assessment relationships, no separate `risks` or `board_decisions` collections, and generic third-party records; the ecosystem YAML is a separate 126-node/108-edge model. | rejected |
| Rendered outputs show no material clipping or overlaps. | All three deck contact sheets and selected full-size slides showed no material clipping or object overlap; however, no independent overflow/collision checker was run or stored. | unresolved |
| Synthetic disclosure is consistently present. | Tests assert the notice in payloads/reports, SVGs include it, and inspected slide footers display it. | confirmed |
| Tool deployment can be treated as control effectiveness. | Slide content, chart standards, and assessment tests retain `UNVALIDATED`, `MEASURE`, `MONITOR`, and `TEST` states and evidence limitations. | rejected |

## What Worked

- The executive system replaced the legacy hairball with task-specific diagrams: a four-group service-to-control-plane dependency map, a ranked concentration chart, an eight-phase scenario timeline, a two-option integrity decision, a current/target recovery comparison, a three-horizon roadmap, and a written-status scorecard. Render inspection showed these views preserve one principal conclusion per slide and avoid the legacy map's crossing pattern.
- Diagram selection matched the question being answered. Layered dependency maps exposed common-mode authority; a bar chart ranked declared counts; a timeline represented scenario order; mirrored current/target columns exposed removed recovery common modes; a roadmap encoded sequence; and a decision list made board actions explicit. These are observed mappings in the decks, not universal preferences.
- Collision control was primarily structural: fixed 1280x720 coordinates, 72-pixel margins, four or fewer top-level service boxes, a single shared dependency box, straight orthogonal-style trunks, connectors created before nodes, short labels, and separate slides for scenario, recovery, investment, and oversight. Selected full-size renders showed no node-label collisions.
- Relationship-count semantics were bounded. The concentration chart displays six categories, directly labels values, and states that counts are neither probability nor loss. Tests recompute the leading value from declared critical relationships.
- Synthetic provenance is visible and machine-checked. Nodes and relationships carry identifiers, owners, criticality, confidence, assumptions, controls, recovery behavior, and a synthetic label; slide evidence identifiers are tested against declared nodes.
- Accessibility corrections that are evidenced include a persistent written synthetic disclosure, text labels in addition to semantic color, SVG `<title>` and `<desc>`, accessible node labels, direct chart labels, a tabular accessibility fallback in the Streamlit assessment UI, and dark-on-light contrast-oriented tokens.
- Material defects caught by tests include duplicate or invalid IDs, unknown relationship endpoints, unsupported high-impact values without rationale, missing synthetic disclosures, missing deck notes, missing masters/layouts, missing or undersized PDF exports, and evidence identifiers that do not resolve to known nodes.

## What Did Not Work

- The legacy wire-transfer graph remained visually unsuitable after deterministic export. It contains roughly two dozen visible nodes, long diagonal edges, edge crossings near the service and application layers, small labels, and excessive whitespace. Staggering some labels did not solve topology or hierarchy.
- The "no hairball" test is currently approximated by `svg.count("<path") < 10`; this does not measure edge crossings, label collisions, or readability. It can pass a poorly arranged diagram.
- The decks' rendered layouts are clean but repetitive and sometimes under-filled. Large unused lower/right regions and repeated bullet/decision compositions reduce information density without adding hierarchy. This is visible in the contact sheets and should not be recorded as validated board preference.
- The 16-point minimum is not consistently enforced in generation. Timeline labels are generated at 13 points, several scorecard labels at 14 points, and the synthetic footer at 10 points. The rendered chart labels are also small. Existing token tests only check the configured body token, not every text object.
- Accessibility evidence is incomplete. The repository declares 4.5:1 contrast, reading order, alternative text, and non-color status encoding, but tests only check token flags and SVG title/description. No stored contrast audit, PowerPoint alt-text audit, reading-order audit, keyboard walkthrough, or grayscale/color-vision render review was found.
- No documented failed-render ledger or before/after slide pair exists. Consequently, specific intermediate layouts that failed inspection cannot be reconstructed beyond the retained legacy network export and current renders.
- PowerPoint generation is coupled to a repository-local `tmp/presentation-build/node_modules` import. This records a tooling compromise: generation depends on a prepared runtime path rather than a portable project dependency contract. The generator exports PNG/layout/inspection files, but the repository does not store evidence from an independent PowerPoint/LibreOffice round trip or an overflow checker.
- The synthetic assessment and ecosystem models overlap but are not one normalized source. The assessment has 12 explicit relationships while the ecosystem has 108, and board decisions are represented as slide recommendations rather than normalized board-decision records. This weakens end-to-end claim provenance.

## Reusable Lessons

- Lesson: Split a dense resilience graph by executive question before changing its visual styling.
- Evidence: The retained wire-transfer network shows crossings and weak hierarchy; rendered service, concentration, scenario, recovery, and decision views are readable at slide scale.
- Applies when: A model contains multiple relationship types, layers, and decision audiences.
- Does not apply when: A small topology has one relationship semantic and remains readable at export size.
- Confidence: high
- Recommended action: Define the decision question first, then select only the records needed for one layered, sequential, matrix, or ranked view; provide a table for the complete relationship set.

- Lesson: Fixed placement prevents collisions only when accompanied by explicit content budgets.
- Evidence: The inspected curated diagrams use four service boxes, one shared dependency box, eight timeline phases, six chart categories, short node labels, and separate slides; no collisions were observed in selected full-size renders.
- Applies when: A board or technical slide is generated from deterministic synthetic data with known upper bounds.
- Does not apply when: Users can add arbitrary records or labels without layout reflow and overflow handling.
- Confidence: medium
- Recommended action: Enforce per-view budgets in code: no more than 4 top-level groups, 6 ranked categories, 8 timeline states, 4 scorecard rows, and 2 lines per node label; switch to filtering or a table when exceeded.

- Lesson: Relationship counts can support concentration discussion if the unit and non-risk interpretation are explicit.
- Evidence: The slide 4 value of seven is recomputed from critical relationships and labeled as dependency evidence, not probability or loss.
- Applies when: Counts come from declared, validated edges with stable inclusion rules.
- Does not apply when: Edge completeness differs materially by domain or counts are presented as likelihood, severity, or capital impact.
- Confidence: high
- Recommended action: Keep the count label, inclusion rule, and caveat adjacent to the chart; require credibility review of model completeness.

- Lesson: Package tests and visual inspection answer different quality questions.
- Evidence: All 64 tests passed while rendered slides still contained text below the declared minimum and visible under-filled layouts.
- Applies when: Presentations are generated programmatically.
- Does not apply when: There is no rendered artifact or the deliverable is data-only.
- Confidence: high
- Recommended action: Retain structural tests, then add rendered font-size, overflow, contrast, crossing, and full-slide review gates with stored evidence.

- Lesson: Accessibility claims require object-level checks, not design-token declarations alone.
- Evidence: Tests validate SVG accessible text and status-token intent but do not inspect PowerPoint alt text, reading order, actual contrast, or every text object's size.
- Applies when: Slides, PDFs, diagrams, and interactive fallbacks are part of one product.
- Does not apply when: A claim is narrowly limited to the verified SVG title/description behavior.
- Confidence: high
- Recommended action: Audit every deck's text sizes, contrast pairs, alt text, reading order, and grayscale legibility; retain the tabular fallback.

- Lesson: Separate synthetic facts, modeled assumptions, and proposed decisions in the data model.
- Evidence: Ecosystem relationships distinguish confidence, assumptions, and propagation, but the assessment lacks normalized risk and board-decision collections and the deck adds recommendations in presentation code.
- Applies when: Claims must trace from source record through analysis to board action.
- Does not apply when: The artifact is explicitly illustrative and makes no traceability claim.
- Confidence: high
- Recommended action: Add stable IDs for risks and board decisions and link each visible claim to node, relationship, evidence, finding, corrective-action, and decision IDs.

## Decisions Made

- Treat the supplied protocol as authoritative because the requested repository protocol files and prior records do not exist; do not invent consensus or overwrite another record.
- Record the lesson as `proposed`, not `validated`, because visual inspection was selective at full size, accessibility validation is incomplete, and no banking reviewer acceptance evidence exists.
- Use the presentation commit `2b51297` as the implementation reference while identifying `61a90f4` as the reviewed working-branch HEAD and `3be8829` as the local integrated-main reference.
- Prefer curated deterministic views over a universal network view. Preserve the network/table exports only as progressive-disclosure or analytical fallbacks.
- Treat relationship counts as modeled dependency evidence only. Do not translate them into risk, probability, expected loss, or investment value.
- Retain explicit synthetic labeling on every audience-facing artifact and require claim-to-record identifiers before treating a board statement as traceable.
- Do not claim that passing tests validates visual accessibility; record the missing object-level and rendered checks as debt.

## Unresolved Questions

- Which branch is the intended baseline for handoff? Local `origin/main` does not include the presentation system, while the reviewed feature branch does.
- Should the 19 Tier 0 records be reduced through service-specific filtering, or is the broad institution-level designation credible to banking architecture reviewers?
- Are the seven identity relationships and four backup relationships complete enough for comparative concentration, or do unequal modeling depths bias the ranking?
- Which recovery statements are demonstrated facts versus target-state requirements, especially independent recovery identity, DNS, telemetry, and offline integrity evidence?
- Can PowerPoint's actual reading order, alt text, and font substitution be verified in the target Microsoft 365 environment?
- Should a normalized `risks` and `board_decisions` model be added, or should those concepts remain findings, corrective actions, approvals, and presentation recommendations?
- What are the approved maximum label length and density thresholds for interactive user-added records?
- Who owns credibility review of regulatory roles, payment obligations, recovery sequence, and third-party substitution assumptions?

## Handoff

The reviewer should challenge the four-group board service taxonomy, the selection of identity as the leading concentration, the institution-specific breadth of 19 Tier 0 designations, the three-horizon investment sequence, and the implication that independent recovery identity/DNS/telemetry are the highest-priority common modes. These are project decisions or synthetic-model interpretations, not externally validated facts.

Slides with the highest remaining uncertainty are executive 4 (ranking depends on relationship-model completeness), executive 6 and tabletop 5 (13-point phase labels and simplified eight-phase causality), executive 9 / technical 8 / tabletop 11 (target recovery architecture is asserted without test evidence), executive 10 / technical 9 / tabletop 13 (investment sequence lacks cost, feasibility, and dependency estimates), and executive 11 / tabletop 12 (status labels are accessible in principle but lack defined measures and actual trend data). The legacy wire-transfer map should not be approved for executive use without redesign.

Synthetic records deserving credibility review include `IF-01` Enterprise identity provider and its seven critical relationships; `IF-17` Backup platform and its four critical relationships; all 19 Tier 0 nodes; propagation records `R-022`, `R-028`, `R-033`, `R-038`, `R-040`, `R-050`, and `R-051`; the `$35B synthetic assets` organization size; generic third-party records `tp-01` through `tp-08`; the clean-room recovery assumptions; the 12 assessment relationships versus 108 ecosystem relationships; and all derived findings/corrective actions that inherit those assumptions.

Tooling compromises to accept, reject, or improve are the hard-coded prepared-runtime import under `tmp/presentation-build/node_modules`, the absence of a stored PowerPoint/LibreOffice round-trip, lack of automated crossing/collision/contrast/read-order tests, small generated labels despite a 16-point token, editable diagrams built from fixed native shapes rather than data-aware reflow, and separate assessment/ecosystem models rather than one normalized traceability graph. Before approval, rerun generation in the target PowerPoint environment, inspect every slide individually at full size, audit accessibility object by object, and add a traceability register that resolves every board claim and decision to synthetic source IDs.
