# Video 5 — Recovery and resilience

**Opening hook:** “A backup can exist and still be unusable if recovery depends on the same identity, DNS, credentials, or corrupted data.”

**Audience outcome:** Understand recovery independence, integrity validation, clean-room prerequisites, and target-state design. **Required state:** checkpoints 8–9 and target-architecture slide. **Expected runtime:** 6:00.

| Time | Narration | On-screen action | Visual insert | On-screen text | Editing note |
| --- | --- | --- | --- | --- | --- |
| 00:00 | Hook. | Integrity dilemma. | Recovery paradox card | BACKUP ≠ RECOVERABILITY | Title 2 seconds |
| 00:40 | Show production identity dependency. | Point to prerequisite column. | Dependency callout | INDEPENDENT IDENTITY | Crop only |
| 01:30 | Explain independent DNS, network, credentials, and time. | Advance to Recovery. | Clean-room diagram | SEPARATE TRUST PLANE | Use native slide |
| 02:30 | Explain data validation before throughput. | Highlight reconciliation row. | Decision card | TRUST BEFORE THROUGHPUT | Pause |
| 03:20 | Explain monitoring during failover. | Insert tool coverage visual. | Limitation | VISIBILITY MUST SURVIVE RECOVERY | No infallibility claim |
| 04:15 | Compare current and target architecture. | Show branded comparison. | Architecture slide | REDUCE COMMON MODE | Clean cut |
| 05:20 | Summarize verification required. | Closing. | Closing | TEST THE WHOLE PATH | Hold |

**Retake points:** backup/recoverability distinction and reconciliation. **Closing:** “Recovery confidence rises only when the complete, independent path is exercised and the restored data is validated.” **Qualification:** the synthetic status is not proof of a production control.
