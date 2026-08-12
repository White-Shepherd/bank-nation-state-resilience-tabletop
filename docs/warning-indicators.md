# Warning indicator catalog

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK. No single weak signal establishes nation-state attribution.**

Each signal record must contain data source, owner, normal baseline, explicit threshold, confidence, benign explanation, corroboration, escalation path, and affected service. Thresholds below are synthetic starting points requiring calibration.

| Domain | Signals | Source / owner | Baseline and threshold | Confidence / benign explanation | Corroboration / escalation / service |
|---|---|---|---|---|---|
| Identity | Privileged-role, new auth method, MFA, break-glass, federation, service account, unusual infrastructure, off-window admin, conditional access, disabled logs | Identity audit / IAM | Approved changes only; alert on any unapproved privileged or logging change | Low-medium; emergency maintenance | PAM, change ticket, endpoint; SOC to IC/CISO; authentication/recovery |
| Control plane | Firewall/routing, DNS, certificate, cloud, virtualization, backup, recovery failure, disabled agent/log degradation/tool config/time anomaly | Config/log platforms / platform owners | Approved window and change; alert on any unapproved high-impact change or 10% critical log loss for 5 min | Medium; automation or maintenance | Independent logs and approvals; SOC to IC/CIO; all mapped services |
| Data integrity | Ledger discrepancy, reconciliation failure, replication anomaly, duplicate/missing/delayed transaction, hash failure, cross-system inconsistency, recovery-point or retention change | Ledger/reconciliation/backup / Finance and Data | Zero unexplained financial variance; alert immediately or when backlog exceeds service tolerance | High for integrity, none for attribution; cutoff timing | Independent totals/source transactions; Finance to IC/CFO; deposits/payments/ledger |
| Network | New outbound, encrypted admin, cross-zone/east-west change, management attempts, simultaneous carrier degradation, DNS failure, network-admin failure | Flow/DNS/carrier / Network | Approved destinations and paths; alert on new admin destination or two carrier impairments | Low-medium; vendor support or routing event | Endpoint, carrier and change records; SOC/NOC to IC; channels/payments/recovery |
| Business | Payment backlog, ATM/card/auth failure, call spike, fraud anomaly, third-party discrepancy, liquidity delay, branch failure, social claim preceding outage | Operations dashboards / service owners | Alert when service-specific backlog/time/customer threshold is reached; social claims require corroboration | Variable; seasonal demand or vendor incident | Technical plus authoritative business data; owner to IC/CRO; named critical service |

