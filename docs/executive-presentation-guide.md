# Executive Presentation System

> **SYNTHETIC EXERCISE DATA - NOT A REAL BANK.**

The presentation layer turns the declared ecosystem model into a board narrative without changing the underlying assessment, scenario, Tier 0, or exercise data. One transformation model supplies the in-application presentation, editable PowerPoint, landscape board PDF, and redesigned repository-safe ecosystem graphic.

## Communication job

By the end, board and executive leaders should approve an evidence-led resilience program because shared identity, administration, recovery, and integrity dependencies can turn a contained technology event into customer, payment, liquidity, and recovery decisions.

## Design system

- Format: 16:9, 1280 by 720 presentation canvas.
- Typography: Aptos in PowerPoint; Arial fallback in SVG; 38 px slide headlines and 19 px supporting copy.
- Palette: deep navy for authority, teal for the narrative path, amber for unvalidated or decision-required conditions, red for modeled failure concentration, green for validated restoration, and slate for context.
- Hierarchy: message title, one supporting sentence, one evidence visual or a short decision list.
- Discipline: relationship counts are labeled as counts, never probability, likelihood, loss, or risk scores.

## Narrative

The 12-slide default sequence moves from stakes to declared concentration, risk and scenario implications, decision ownership, Tier 0 boundaries, recovery prerequisites, investment priorities, oversight evidence, and a board decision. The same model can support executive, risk, technical, incident-command, and recovery variants without creating a separate source of truth.

## Generate outputs

From the repository root:

```powershell
python scripts/generate_presentation_assets.py
node scripts/generate_executive_presentation.mjs
```

The PowerPoint generator requires the bundled Codex presentation runtime prepared under `tmp/presentation-build`. The generated files are:

- `output/presentation/harbor-ridge-executive-resilience-briefing.pptx`
- `output/pdf/harbor-ridge-executive-resilience-briefing.pdf`
- `docs/images/high-level-banking-ecosystem.svg`
- slide PNG previews and layout diagnostics under `tmp/presentation-build/previews/`

Run `streamlit run app.py` and open **Executive presentation** for the coordinated in-app view and downloads.

## Review checklist

Confirm message-driven titles, readable type, synthetic labeling, evidence identifiers, no unexplained attribution, no unsupported propagation, and no clipped or overlapping objects. Inspect every rendered slide and PDF page after changing content or typography.
