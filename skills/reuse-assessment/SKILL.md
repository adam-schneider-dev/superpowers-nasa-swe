---
name: reuse-assessment
description: Use to record a suitability assessment for each COTS/GOTS/MOTS/OSS or reused software component per NPR 7150.2D §3.10
---

# Software Reuse Assessment (NPR 7150.2D §3.10)

## Overview

Walks §3.10.2's (SWE-148) suitability conditions for a reused, COTS, GOTS, MOTS, or OSS software component, one assessment per component. Run once per component being evaluated — each run appends its own entry to the record.

**Announce at start:** "I'm using the reuse-assessment skill to record a software reuse assessment."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview (per component)

Per SWE-148, record at minimum:

1. **Software title and description** — what is the component, and what does it do in this project?
2. **Technical POC** — who is the civil servant technical point of contact for this software product?
3. **Language(s)** — what language(s) was it developed in?
4. **Third-party licensing** — any third-party code within it, and the license/permission record for NASA's use, including required copyright/author/license notices and the source URL(s) if applicable.
5. **Release notes** — a pointer to them, if the component has its own release notes.
6. **Reusability of this project's own output (§3.10.1, SWE-147)** — does this project's own software specify reusability requirements so it, in turn, can be reused by others?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/reuse-assessment/scripts
python3 -c "
from record_reuse_assessment import record_reuse_assessment

record_reuse_assessment(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's reuse-assessment.md>',
    swe_ids=['SWE-147', 'SWE-148'],
    fields={
        'component_name': '<answer to question 1>',
        'description': '<answer to question 1>',
        'technical_poc': '<answer to question 2>',
        'language': '<answer to question 3>',
        'third_party_license_info': '<answer to question 4>',
        'release_notes': '<answer to question 5>',
    },
    evidence='<pointer to the license/permission record>',
)
print('Recorded.')
"
```

Repeat for each additional component being assessed.

## Writing the output

Confirm to the user which component was recorded and where. Note that `SWE-147`/`SWE-148` get marked satisfied on the first successful assessment — the record file itself lists every component assessed since, so a later reviewer sees the full history, not just the latest.
