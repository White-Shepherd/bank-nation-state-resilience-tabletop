# Defensive threat model

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK**

The fictional actor seeks operational disruption, financial-data corruption, confidence loss, payment interruption, destructive effects, recovery interference, intelligence collection, third-party access, and narrative manipulation. Attribution remains uncertain: behavior, infrastructure, intent, and government/sector reporting must be corroborated.

Defensive MITRE ATT&CK behaviors include valid accounts (T1078), account manipulation (T1098), cloud account activity (T1098.003), network service discovery (T1049), remote services (T1021), inhibit system recovery (T1490), service stop (T1489), data destruction (T1485), data manipulation (T1565), endpoint denial of service (T1499), and supply-chain compromise (T1195). These mappings guide telemetry and resilience tests; they are not intrusion instructions or claims that the synthetic evidence establishes any technique or actor.

Trust boundaries include customer-to-channel, workforce-to-administration, bank-to-processor/network, production-to-recovery, and authoritative-ledger-to-reporting. Defensive priorities are independent identity and telemetry, change validation, immutable evidence, reconciliation, segmentation, minimum viable payments, alternate communications, and clean recovery.

