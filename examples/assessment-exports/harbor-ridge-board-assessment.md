# SYNTHETIC DEMONSTRATION DATA - NOT A REAL BANK ASSESSMENT

# Board assessment packet

## Executive summary

Harbor Ridge Critical-Service Assessment identifies 12 critical services. Automated analysis recommends candidates and findings for accountable human review; it does not replace business, risk, legal, compliance, audit, or board judgment.

## Assessment scope

Harbor Ridge Bank; Fictional regional banking; classification: Internal.

## Critical services

- Customer authentication: Outcome disruption can harm customers or market obligations.
- Account inquiry: Outcome disruption can harm customers or market obligations.
- Core deposit processing: Outcome disruption can harm customers or market obligations.
- ACH: Outcome disruption can harm customers or market obligations.
- Wire transfers: Outcome disruption can harm customers or market obligations.
- Card authorization: Outcome disruption can harm customers or market obligations.
- Card settlement: Outcome disruption can harm customers or market obligations.
- ATM withdrawals: Outcome disruption can harm customers or market obligations.
- Treasury management: Outcome disruption can harm customers or market obligations.
- Fraud monitoring: Outcome disruption can harm customers or market obligations.
- Liquidity reporting: Outcome disruption can harm customers or market obligations.
- Regulatory reporting: Outcome disruption can harm customers or market obligations.

## Approved impact tolerances

- svc-01: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-02: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-03: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-04: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-05: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-06: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-07: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-08: MTD 240m; RTO 120m; RPO 15m; approved=True
- svc-09: MTD 480m; RTO 240m; RPO 15m; approved=False
- svc-10: MTD 480m; RTO 240m; RPO 15m; approved=False
- svc-11: MTD 480m; RTO 240m; RPO 15m; approved=False
- svc-12: MTD 480m; RTO 240m; RPO 15m; approved=False

## Tier 0 candidates

- enterprise-identity: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- directory: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- pam: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- dns: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- time: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- certificates: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cloud-control: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, no-practical-substitute; decision=Pending
- network-control: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, no-practical-substitute; decision=Pending
- virtualization: supports-multiple-critical-services, broad-administrative-authority; decision=Pending
- database-control: supports-multiple-critical-services, broad-administrative-authority; decision=Pending
- backup: supports-multiple-critical-services, trustworthy-recovery-dependency; decision=Pending
- recovery: supports-multiple-critical-services, trustworthy-recovery-dependency; decision=Pending
- telecom-a: supports-multiple-critical-services; decision=Pending
- dc-primary: supports-multiple-critical-services; decision=Pending
- cloud-region: supports-multiple-critical-services; decision=Pending
- admin-endpoints: supports-multiple-critical-services; decision=Pending
- logging: supports-multiple-critical-services; decision=Pending
- security-console: supports-multiple-critical-services; decision=Pending
- clean-room: supports-multiple-critical-services, trustworthy-recovery-dependency; decision=Pending
- offline-vault: supports-multiple-critical-services, trustworthy-recovery-dependency; decision=Pending
- cp-enterprise-identity: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-directory: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-pam: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-dns: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-time: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-certificates: supports-multiple-critical-services, broad-administrative-authority, trustworthy-recovery-dependency, no-practical-substitute; decision=Pending
- cp-cloud-control: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, no-practical-substitute; decision=Pending
- cp-network-control: supports-multiple-critical-services, broad-administrative-authority, control-plane-authority, no-practical-substitute; decision=Pending
- cp-virtualization: supports-multiple-critical-services, broad-administrative-authority; decision=Pending
- cp-database-control: supports-multiple-critical-services, broad-administrative-authority; decision=Pending

## Material concentrations

- Shared Identity concentration
- Shared Directory concentration
- Shared Privileged access concentration
- Shared DNS concentration
- Shared Time concentration
- Shared Certificates concentration
- Shared Cloud management concentration
- Shared Network management concentration
- Shared Virtualization concentration
- Shared Database concentration
- Shared Backup concentration
- Shared Recovery concentration
- Shared Telecommunications concentration
- Shared Data center concentration
- Shared Cloud region concentration
- Shared Endpoint concentration
- Shared Logging concentration
- Shared Security concentration
- Shared Recovery concentration
- Shared Recovery concentration
- Third-party concentration without substitution
- Third-party concentration without substitution
- Third-party concentration without substitution
- Third-party concentration without substitution

## Recovery-readiness findings

- Recovery depends on production control
- Recovery depends on production control
- Recovery depends on production control
- Recovery depends on production control
- Recovery depends on production control
- Recovery depends on production control
- Recovery depends on production control
- Shared Recovery concentration
- Recovery depends on production control
- Shared Recovery concentration
- Shared Recovery concentration
- Manual workaround absent or untested
- Manual workaround absent or untested
- Manual workaround absent or untested
- Manual workaround absent or untested
- Manual workaround absent or untested
- Manual workaround absent or untested

## Third-party dependencies

- Core service provider: Synthetic core service provider service; recovery evidence: Never
- Payment processor: Synthetic payment processor service; recovery evidence: 2026 synthetic test
- Cloud provider: Synthetic cloud provider service; recovery evidence: 2026 synthetic test
- Telecommunications provider: Synthetic telecommunications provider service; recovery evidence: Never
- Managed security provider: Synthetic managed security provider service; recovery evidence: 2026 synthetic test
- Card network liaison: Synthetic card network liaison service; recovery evidence: 2026 synthetic test
- ACH operator liaison: Synthetic ach operator liaison service; recovery evidence: Never
- Recovery support firm: Synthetic recovery support firm service; recovery evidence: 2026 synthetic test

## Security-coverage gaps

- Security event monitoring: maturity 1/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Endpoint detection: maturity 2/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Network detection: maturity 3/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Identity threat detection: maturity 4/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Fraud detection: maturity 5/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Cloud monitoring: maturity 1/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Vulnerability management: maturity 2/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Backup-integrity validation: maturity 3/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.
- Configuration monitoring: maturity 4/8; limitation: Coverage and testing vary; tool ownership does not guarantee effectiveness.

## Manual-workaround limitations

- Customer authentication manual continuity: throughput 0%; test: Requires improvement
- Account inquiry manual continuity: throughput 25%; test: Requires improvement
- Core deposit processing manual continuity: throughput 25%; test: Requires improvement
- ACH manual continuity: throughput 25%; test: Requires improvement
- Wire transfers manual continuity: throughput 0%; test: Requires improvement
- Card authorization manual continuity: throughput 25%; test: Requires improvement
- Card settlement manual continuity: throughput 25%; test: Requires improvement
- ATM withdrawals manual continuity: throughput 25%; test: Requires improvement
- Treasury management manual continuity: throughput 0%; test: Requires improvement
- Fraud monitoring manual continuity: throughput 25%; test: Requires improvement
- Liquidity reporting manual continuity: throughput 25%; test: Requires improvement
- Regulatory reporting manual continuity: throughput 25%; test: Requires improvement

## Recommended tabletop scenarios

- Enterprise identity compromise: Applies to synthetic shared dependencies and evidence-based gaps.
- Payment processor outage: Applies to synthetic shared dependencies and evidence-based gaps.
- Cloud-region failure: Applies to synthetic shared dependencies and evidence-based gaps.
- Data-integrity uncertainty: Applies to synthetic shared dependencies and evidence-based gaps.
- Backup compromise: Applies to synthetic shared dependencies and evidence-based gaps.

## Corrective-action roadmap

- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Establish and test independent recovery control. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Validate separation and an alternate capability. (Chief Risk Officer)
- [High] Test exit, substitution, or manual continuity. (Chief Risk Officer)
- [High] Test exit, substitution, or manual continuity. (Chief Risk Officer)
- [High] Test exit, substitution, or manual continuity. (Chief Risk Officer)
- [High] Test exit, substitution, or manual continuity. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)
- [High] Exercise the minimum viable manual service and reconciliation. (Chief Risk Officer)

## Decisions required

- Review enterprise-identity Tier 0 classification
- Review directory Tier 0 classification
- Review pam Tier 0 classification
- Review dns Tier 0 classification
- Review time Tier 0 classification
- Review certificates Tier 0 classification
- Review cloud-control Tier 0 classification
- Review network-control Tier 0 classification
- Review virtualization Tier 0 classification
- Review database-control Tier 0 classification
- Review backup Tier 0 classification
- Review recovery Tier 0 classification
- Review telecom-a Tier 0 classification
- Review dc-primary Tier 0 classification
- Review cloud-region Tier 0 classification
- Review admin-endpoints Tier 0 classification
- Review logging Tier 0 classification
- Review security-console Tier 0 classification
- Review clean-room Tier 0 classification
- Review offline-vault Tier 0 classification
- Review cp-enterprise-identity Tier 0 classification
- Review cp-directory Tier 0 classification
- Review cp-pam Tier 0 classification
- Review cp-dns Tier 0 classification
- Review cp-time Tier 0 classification
- Review cp-certificates Tier 0 classification
- Review cp-cloud-control Tier 0 classification
- Review cp-network-control Tier 0 classification
- Review cp-virtualization Tier 0 classification
- Review cp-database-control Tier 0 classification

## Residual uncertainties

- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending
- Exercise outcome pending

## Evidence limitations

- enterprise-identity: Monitoring detection has not been tested
- dns: Monitoring detection has not been tested
- cloud-control: Monitoring detection has not been tested
- database-control: Monitoring detection has not been tested
- telecom-a: Monitoring detection has not been tested
- admin-endpoints: Monitoring detection has not been tested
- clean-room: Monitoring detection has not been tested
- data-10: Authoritative-data status is unclear
- data-12: Authoritative-data status is unclear
- backup: Synthetic validation evidence is unavailable
- tp-01: Synthetic validation evidence is unavailable
- work-01: Synthetic validation evidence is unavailable