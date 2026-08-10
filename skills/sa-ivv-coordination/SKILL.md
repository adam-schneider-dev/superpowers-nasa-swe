---
name: sa-ivv-coordination
description: Use to record a subsystem's assigned software assurance, software safety, and IV&V roles and plan per NPR 7150.2D §3.6
---

# Software Assurance and IV&V Coordination (NPR 7150.2D §3.6)

## Overview

Records the SA, software safety, and IV&V roles assigned to the subsystem and the plan reference §3.6.1 requires. Does not perform SA or IV&V itself — that's real engineering/assurance work this tool doesn't replace.

**Announce at start:** "I'm using the sa-ivv-coordination skill to record your NPR 7150.2D §3.6 software assurance and IV&V coordination."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Roles (§3.6.1, SWE-022).** Who is assigned as software assurance lead, software safety lead, and (if applicable) IV&V provider for this subsystem?
2. **Plan (§3.6.1, SWE-022).** Point to the Software Assurance Plan (per NASA-HDBK-2203's recommended content, including software safety). If none exists yet, say so — do not fabricate a pointer.
3. **IV&V applicability (§3.6.2, SWE-141).** Is this subsystem in a category NPR 7120.5 or a Mission Directorate Associate Administrator decision would require IV&V on (e.g. Category 1 projects, or Category 2 with Class A/B payload risk)? If yes and IV&V hasn't been engaged, tell the user this is a gap, don't silently mark it satisfied.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/sa-ivv-coordination/scripts
python3 -c "
from record_sa_ivv_coordination import record_sa_ivv_coordination

record_sa_ivv_coordination(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's sa-ivv-coordination.md>',
    swe_ids=['SWE-022'],
    fields={
        'sa_safety_ivv_roles': '<answer to question 1>',
        'plan_reference': '<answer to question 2>',
        'ivv_applicability': '<answer to question 3>',
    },
    evidence='<the plan document's path>',
)
print('Recorded.')
"
```

If there's no plan to point to yet, don't run the script — tell the user the row stays `not-started` until one exists.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
