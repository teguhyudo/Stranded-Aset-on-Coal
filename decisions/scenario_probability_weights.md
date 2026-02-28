# Scenario Probability Weights: Rationale and Sensitivity

## Decision

Assign scenario probability weights of BAU = 0.30, 2C = 0.40, 1.5C = 0.30 for the expected stranded value calculation.

## Context

The NGFS provides reference climate scenarios (Current Policies, Below 2C, Net Zero 2050, etc.) but does **not** prescribe probability weights. These scenarios are designed as "what-if" explorations of alternative policy trajectories, not probabilistic forecasts. No consensus exists in the literature on how to assign probabilities to long-term climate policy outcomes.

## Rationale for Current Weights

The 2C scenario receives the highest weight (0.40) for three reasons:

1. **Median policy ambition.** The 2C pathway is broadly consistent with current Nationally Determined Contribution (NDC) trajectories under the Paris Agreement. While most NDCs collectively fall short of the 1.5C target, they represent meaningful policy action beyond business-as-usual. The 2C scenario thus approximates the median policy outcome conditional on existing commitments being honoured.

2. **Market-implied expectations.** Carbon futures pricing and forward coal price curves as of 2024-2025 embed expectations more consistent with a gradual transition than with either policy inaction (BAU) or rapid decarbonisation (1.5C).

3. **Symmetric tails.** Assigning equal weight (0.30) to BAU and 1.5C treats upside policy ambition and downside policy failure as equally likely, which is a defensible neutral prior.

## Uncertainty Treatment

The Monte Carlo simulation (10,000 draws) samples scenario weights from a Dirichlet(3, 4, 3) distribution, which centres on (0.30, 0.40, 0.30) but allows for substantial variation across draws. This approach captures probability uncertainty without requiring point estimates to be definitive.

## Sensitivity Results

The tornado diagram (Figure 10) shows that scenario probability weights have the **smallest impact** on aggregate stranded value among all parameters tested:

- Range: -2.5 to +3.1 billion USD
- By comparison, the discount rate produces a range of approximately +/- 15% of baseline SV

This finding is intuitive: the expected SV is a weighted average bounded by the 2C and 1.5C point estimates, so shifting weights within reasonable bounds produces modest changes.

**Implication:** Our key conclusions are robust to alternative probability assignments.

## Alternative Approaches Considered

| Approach | Description | Why Not Adopted |
|----------|-------------|-----------------|
| Equal weights (1/3 each) | Agnostic prior | Ignores information from current policy trajectories |
| Climate Action Tracker implied weights | Based on CAT's assessment of current policies vs. pledges vs. targets | CAT does not provide formal probability distributions |
| Expert elicitation (Pindyck 2019) | Survey climate economists for subjective probabilities | Resource-intensive; no Indonesia-specific elicitation available |
| Market-implied from carbon futures | Back out scenario probabilities from carbon price term structure | Indonesian carbon market too nascent; limited liquidity |

## Manuscript Updates

- Section 5 (Model 1), line 55: Softened language from "consistent with NGFS" to "reflecting the authors' assessment informed by NGFS reference pathways"
- Section 8 (Discussion): Added note that 2C is the median policy pathway and weight sensitivity is minimal
- Decision log updated

## References

- NGFS (2022). NGFS Climate Scenarios for central banks and supervisors. Phase IV.
- Pindyck, R.S. (2019). The social cost of carbon revisited. Journal of Environmental Economics and Management.
- IEA (2023). World Energy Outlook 2023.
