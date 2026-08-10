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
)
print(yaml.dump(result, sort_keys=False))
"
```

If the script raises `ValueError` mentioning "conflicting", **stop and surface it to the user** rather than re-running with a different answer to make it pass — either a prior run or `classify-software`'s original determination already recorded a class-changing answer that disagrees, and the disagreement itself needs a human decision, not code that papers over it.

## Writing the output

Overwrite `docs/nasa-compliance/<subsystem>/classification.yaml` with the printed YAML. If `class` changed as a result (e.g. Class E → D), tell the user the Requirements Mapping Matrix is now stale and they should re-run `requirements-matrix` to regenerate it.

**Warn the user before they regenerate:** regeneration rewrites the matrix from the catalog and **resets every row's status to `not-started`**, with `evidence` and `date` cleared — there is no merge with the existing file, so anything already recorded (`satisfied` rows, `tailored-out` rows, evidence pointers) is lost. `tailoring-log.md` is *not* touched by regeneration, so a regenerated matrix can end up disagreeing with the tailoring log it is supposed to match. Tell the user to note down every already-recorded row first (id, status, evidence, date) and re-apply them after regenerating, because nothing preserves them automatically. Each regenerated row carries a `software_class` stamp, which is how a stale matrix can be spotted later — compare it against `classification.yaml`'s `class`.

## Marking the matrix row

Do this **after** any regeneration above — marking a row in a matrix that is about to be discarded accomplishes nothing.

Run `mark_matrix_satisfied` against the subsystem's `requirements-mapping-matrix.yaml` for `SWE-205` (§3.7.1, the determination requirement itself):

```bash
cd <this-plugin's-install-path>/skills/safety-critical-determination/scripts
python3 -c "
from amend_safety_critical import mark_matrix_satisfied

mark_matrix_satisfied(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    swe_id='SWE-205',
    evidence='<pointer to this run's rationale in classification.yaml>',
)
print('Recorded.')
"
```

If `SWE-205` isn't present in the matrix, work out which of three cases applies before reporting it: the subsystem's class genuinely has no §3.7.1 row (Appendix C does not invoke `SWE-205` on every class — for such a class this is correct behaviour, not a gap, and safety-critical determination via `SWE-205` simply isn't tracked there); the matrix predates a class change and needs regenerating; or the catalog is missing the row. Tell the user which one it is rather than silently skipping it — and don't send a user whose class has no §3.7.1 row hunting for a bug that isn't there.
