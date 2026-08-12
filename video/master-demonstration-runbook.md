# Master demonstration runbook

## Locked recording state

Record branch and commit from `git branch --show-current` and `git rev-parse --short HEAD` on the slate immediately before capture. Use Python 3.10 or newer in `.venv`; start with `streamlit run app.py`. Record at 1920×1080 or higher, 100% Windows scaling, browser zoom 100%, 30 fps, and a 48 kHz microphone track. Load only `data/synthetic_assessments/harbor-ridge-2026.json` through Demo Mode.

Before recording, generate or verify `presentations/board/executive-resilience-briefing.pdf` and `examples/board-packet/board-packet.pdf`. Open only the Streamlit tab, script, and final PDF. Close email, chat, cloud-drive, password-manager, and personal tabs; hide bookmarks; disable operating-system, browser, calendar, and phone notifications. Remove account avatars, usernames, local paths, recent-file lists, and recording-software account panels from frame.

## Master timeline (target 46:00)

| Time | Checkpoint | Presenter objective | Transition marker |
| --- | --- | --- | --- |
| 00:00–04:00 | Overview | Establish service-led resilience problem and outputs | “Now I’ll build from the service outward.” |
| 04:00–08:00 | Critical service | Define wire transfers and accountable ownership | 2 seconds silence |
| 08:00–12:00 | Impact tolerance | Explain MTD, RTO, RPO, minimum viable service | “A target is not proof.” |
| 12:00–18:00 | Dependency map | Trace process, data, identity, providers | 2 seconds silence |
| 18:00–23:00 | Tier 0 | Explain rules and human approval boundary | “Next, concentration.” |
| 23:00–27:00 | Concentration finding | Connect common mode to services and evidence | 2 seconds silence |
| 27:00–32:00 | Scenario warning | Show weak signals without attribution | “The evidence is now decision-relevant.” |
| 32:00–37:00 | Integrity dilemma | Record one containment decision and deadline | 3 seconds silence |
| 37:00–42:00 | Recovery | Validate identity, DNS, data, reconciliation | “Recovery is a trust decision.” |
| 42:00–46:00 | Board packet | Show actions, owners, uncertainty, investment | End slate, 5 seconds silence |

## Exact sequence

Run `python scripts/video_preflight.py`; record its PASS summary as a private production artifact, not in the final cut. Enable Demo Mode, reset, and advance with **Next checkpoint**. At the integrity dilemma select **Isolate production identity and preserve independent recovery access**. Do not edit canonical data. At Board packet, open the preview and download only if the browser download shelf is hidden.

## Backup plan

Record application and microphone to separate tracks when supported. Preserve the untouched master, immediately copy it to a second local drive, then record pickups as isolated sentences with five seconds of room tone. If the app fails, stop; save the recording; restart Streamlit; reset Demo Mode; resume at the named checkpoint. Never substitute a mock screen.

## Qualification language

Say “synthetic,” “candidate,” “demonstrated,” “declared relationship,” and “requires human approval.” Do not say the platform prevents attacks, proves recovery, attributes an actor, predicts loss, or produced real customer outcomes.
