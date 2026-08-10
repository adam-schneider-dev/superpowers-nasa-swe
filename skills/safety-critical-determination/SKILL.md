---
name: safety-critical-determination
description: Use once a subsystem is classified, to perform NPR 7150.2D §3.7 / NASA-STD-8739.8B §4.2's full safety-critical software determination and reconcile it with classify-software's classification.yaml, the one authoritative record
---

# Safety-Critical Software Determination (NPR 7150.2D §3.7, NASA-STD-8739.8B §4.2)

## Overview

`classify-software` already asks a lightweight safety-critical question to apply Appendix D's Class-E exclusion. This skill runs the fuller §3.7 / §4.2 determination — per SWE-205, done by the project manager "in conjunction with the SMA organization," not by engineering alone — and keeps `classification.yaml` as the one authoritative record rather than writing a second file that could disagree with it.

**Announce at start:** "I'm using the safety-critical-determination skill to run NPR 7150.2D §3.7's safety-critical software determination."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/classification.yaml` to already exist (produced by `classify-software`). If it doesn't exist, stop and run that skill first.

## The determination

Per NASA-STD-8739.8B §4.2, software is safety-critical if it is determined by, and traceable to, a hazard analysis to meet at least one of:

a. Causes or contributes to a system hazardous condition/event.
b. Controls functions identified in a system hazard.
c. Provides mitigation for a system hazardous condition/event.
d. Mitigates damage if a hazardous condition/event occurs.
e. Detects, reports, and takes corrective action if the system reaches a potentially hazardous state.

Ask the user to confirm this was assessed against an actual hazard analysis, not a guess, and — per SWE-205 — that the SMA organization concurred. If no hazard analysis exists yet, say so and stop rather than recording a guess.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/safety-critical-determination/scripts
python3 -c "
import sys, os, yaml
sys.path.insert(0, os.path.join(os.getcwd(), '..', '..', 'classify-software', 'scripts'))
from amend_safety_critical import amend_safety_critical

with open('<path to subsystem's classification.yaml>') as f:
    classification = yaml.safe_load(f)

result = amend_safety_critical(
    classification,
    is_safety_critical=<True/False from the determination above>,
    rationale='<one paragraph citing which of a-e matched, or why none did>',
    date='<today, YYYY-MM-DD>',
)
print(yaml.dump(result, sort_keys=False))
"
```

If the script raises `ValueError` mentioning "conflicting", **stop and surface it to the user** rather than re-running with a different answer to make it pass — a prior run already recorded a rationale-backed determination that disagrees, and the disagreement itself needs a human decision, not code that papers over it.

## Writing the output

Overwrite `docs/nasa-compliance/<subsystem>/classification.yaml` with the printed YAML. If `class` changed as a result (e.g. Class E → D), tell the user the Requirements Mapping Matrix is now stale and they should re-run `requirements-matrix` to regenerate it.

## Marking the matrix row

Run `mark_matrix_satisfied` against the subsystem's `requirements-mapping-matrix.yaml` for `SWE-205` (§3.7.1, the determination requirement itself):

```bash
python3 -c "
from amend_safety_critical import mark_matrix_satisfied

mark_matrix_satisfied(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    swe_id='SWE-205',
    evidence='<pointer to this run's rationale in classification.yaml>',
    date='<today, YYYY-MM-DD>',
)
print('Recorded.')
"
```

If `SWE-205` isn't present in the matrix (catalog gap, or the matrix predates the class change), tell the user rather than silently skipping it.
