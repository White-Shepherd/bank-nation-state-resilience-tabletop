# Wire transfers Dependency Report

**SYNTHETIC EXERCISE DATA - NOT A REAL BANK**

Owner: Payment Operations
Tier 0: False

## Declared relationships
- CBS-05 **depends_on** BP-01: Wires require initiation (high)
- CBS-05 **depends_on** BP-02: Wires require dual approval (high)
- CBS-05 **depends_on** BP-03: Wires require sanctions screening (medium)
- CBS-05 **depends_on** BP-04: Wires require risk-based fraud review (medium)
- IP-14 **operates** CBS-05: Payment operations operates wire service (medium)
- EP-09 **supplies** CBS-05: Correspondent banks support settlement and liquidity (medium)