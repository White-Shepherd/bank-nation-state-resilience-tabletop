# Failure propagation methodology

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK**

Propagation occurs only when `propagation: true` is declared on a relationship. The explanation includes trigger, dependency, service effect, confidence, assumptions, and compensating control. The engine performs a bounded single pass; it does not recursively invent cascading failure. Dependency cycles are detected and displayed so reviewers can distinguish valid mutual dependencies from modeling errors.

