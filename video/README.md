# Continuum Resilience video-production system

This package supports one presenter recording a 40–50 minute master demonstration on Windows, then cutting six feature videos, an 8–10 minute portfolio reel, and short clips. Every screen uses the working application and the canonical fictional Harbor Ridge data.

## Start

1. Activate the project environment and run `streamlit run app.py`.
2. Run `python scripts/video_preflight.py` in a second terminal.
3. Enable **Demo Mode** in the sidebar and select **Reset demonstration**.
4. Record checkpoints 1–10 in order using [the master runbook](master-demonstration-runbook.md).

The raw recording and local pickup files belong in `video/recordings/`, which is ignored by Git. Do not record a private assessment.

## Package map

- `scripts/`: timed narration and screen actions for each deliverable.
- `storyboards/`: frame-by-frame visual plans linked to evidence.
- `shot-lists/`: master capture and pickup coverage.
- `captions/`: caption style and reusable disclosure copy.
- `thumbnails/`: branded SVG thumbnail templates.
- `assets/`: title, lower-third, decision, qualification, phase, and closing overlays.
- `evidence-index.md`: claim-to-code/input/output traceability.
- `checkpoint-evidence.md`: expected state, screenshot, claim, limitation, and reset instruction for every checkpoint.

All product claims describe demonstrated behavior, not customer outcomes or control effectiveness.
