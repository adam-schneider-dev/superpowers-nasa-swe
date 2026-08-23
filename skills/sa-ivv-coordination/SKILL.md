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

If the subsystem's class has no rows for this section in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check the matrix first; the example ids below are illustrative of a class that does carry §3.6 rows.

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

## If IV&V applies (§3.6.2, SWE-141 answered yes)

Generate this subsystem's IV&V verification matrix — the separate `ivv-verification-record` skill (NASA-STD-8739.8B §4.4.2) needs it to record the 49 IV&V provider verification requirements. Skip this section entirely if question 3's answer was no; do not generate an empty or placeholder matrix for a subsystem that doesn't require IV&V.

```bash
cd <this-plugin's-install-path>/skills/sa-ivv-coordination/scripts
python3 -c "
import yaml
from ivv_matrix import render_ivv_matrix_markdown, render_ivv_matrix_status_yaml

with open('../../../data/ivv-catalog.yaml') as f:
    catalog = yaml.safe_load(f)

subsystem = '<subsystem name>'
md = render_ivv_matrix_markdown(catalog, subsystem)
status_rows = render_ivv_matrix_status_yaml(catalog)

print(md)
print('---STATUS-YAML---')
print(yaml.dump(status_rows, sort_keys=False))
"
```

Write the printed markdown to `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml` in the project being worked on — the same two-file pattern `requirements-matrix` uses for the main matrix. All 49 rows start `not-started`; nothing here is filtered by class, since every row applies once IV&V is confirmed applicable.
