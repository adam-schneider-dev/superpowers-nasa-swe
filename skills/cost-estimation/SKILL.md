---
name: cost-estimation
description: Use to record a subsystem's NPR 7150.2D §3.2 software cost estimate — methodology, basis of estimate, and size/effort parameters — without computing the estimate itself
---

# Software Cost Estimation (NPR 7150.2D §3.2)

## Overview

Records the cost-estimation artifacts §3.2 requires: methodology and model count, basis of estimate, and the size/effort parameters §3.2.3 requires reporting to the Center measurement repository. **Does not compute an estimate** — NPR 7150.2D doesn't mandate a specific cost model, and inventing numbers would be worse than not having this skill.

**Announce at start:** "I'm using the cost-estimation skill to record your NPR 7150.2D §3.2 cost estimation basis."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and `.../classification.yaml` to already exist.

## The interview

1. **Model count (§3.2.1, SWE-015).** Per NPR 7150.2D: Class A/B projects ≥$2M need two independent cost estimate models; Class A/B under $2M, and all Class C/D/F projects, need one. Confirm the subsystem's class (from `classification.yaml`) and estimated cost, and how many models were actually used.
2. **Basis of estimate (§3.2.2, SWE-151).** Point to the actual estimate document — it must cover the full life cycle and be based on real project attributes (size, complexity, criticality, reuse, risk), not just a number. If no estimate exists yet, say so and stop for this question — do not fabricate a basis.
3. **Size/effort parameters (§3.2.3, SWE-174).** What size and effort figures (and their basis) were or will be submitted to the Center measurement repository?

## Running the script

If the subsystem's class has no rows for this section in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check the matrix first: the example ids below are illustrative of a class that does carry §3.2 rows, and Appendix C invokes no §3.2 Cost Estimation rows at all on Class E.

```bash
cd <this-plugin's-install-path>/skills/cost-estimation/scripts
python3 -c "
from record_cost_estimation import record_cost_estimation

record_cost_estimation(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's cost-estimation.md>',
    swe_ids=[<SWE-ids answered with a real artifact, e.g. 'SWE-015', 'SWE-151', 'SWE-174'>],
    fields={
        'methodology': '<answer to question 1>',
        'basis_of_estimate': '<answer to question 2>',
        'size_and_effort_parameters': '<answer to question 3>',
    },
    evidence='<the estimate document's path>',
)
print('Recorded.')
"
```

If no estimate exists at all, do not run the script — tell the user this subsystem has no cost estimation basis to record yet, and that the matrix rows will stay `not-started` until one exists.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
