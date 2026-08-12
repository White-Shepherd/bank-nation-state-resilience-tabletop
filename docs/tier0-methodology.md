# Tier 0 methodology

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK**

Tier 0 is Harbor Ridge Bank's operational designation for a service, system, identity, control plane, data set, facility, person, or third party whose loss or corruption could stop critical banking, control the wider environment, prevent trustworthy multi-service recovery or reconciliation, exceed MTD, cause material customer harm, impede settlement, or create material liquidity, capital, legal, or safety effects. It is neither universally mandatory nor a NIST CSF Implementation Tier.

Start with the 16 business services in `data/critical_services/services.yaml`. Owners approve impact tolerances; RTO remains a recovery target inside MTD and is not interchangeable with it. Map applications, databases, identity/PAM/domain/DNS/keys, network/cloud/virtualization, backup/orchestration/time/monitoring/endpoints, carriers/facilities/people, third parties/payment networks/data feeds/reconciliation.

Review common modes: a single identity or PAM platform, shared credentials/network management/DNS/certificates/cloud region/carrier/processor, production-controlled backup and recovery, corruption-replicating recovery, and monitoring dependent on the monitored environment.

A candidate qualifies for accountable review if at least one rule is supported by evidence: it can stop multiple critical services, grants broad administration, is necessary for trusted recovery, or is authoritative for financial integrity. The rule does not approve the asset. Business and technical owners document rationale, gaps, recovery, evidence, validation date, and approval status; risk and architecture challenge the decision at least annually and after material change.

