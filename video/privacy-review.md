# Recording privacy review

## Scope and result

The designed Demo Mode reads only the tracked canonical Harbor Ridge assessment and exposes no private-assessment selector, persistence control, local path, or developer control. Canonical data remains read-only because the presenter surface has no save, edit, import, archive, or delete action. This is an implementation property, not a guarantee that the recording environment contains no personal material.

## Reviewer checks

- [ ] Synthetic banner visible at every checkpoint.
- [ ] No private assessment selected or shown in browser history.
- [ ] No local filesystem path, username, email, token, secret, account avatar, bookmark, or notification visible.
- [ ] No real institution, vendor architecture, customer data, incident, finding, or result stated.
- [ ] Downloads and recent-file panels remain outside frame.
- [ ] Audio contains no names or information not present in the synthetic repository.
- [ ] Captions preserve qualifications and do not introduce stronger claims.

Run `python scripts/video_preflight.py`. Its repository scan is a narrow backstop, not a substitute for frame-by-frame and audio review of the final export.
