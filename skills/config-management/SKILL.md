---
name: config-management
description: Use to record a subsystem's NPR 7150.2D §5.1 software configuration management plan, mechanisms, and evidence
---

# Software Configuration Management (NPR 7150.2D §5.1)

## Overview

Records the software configuration management plan and the mechanisms it establishes — change tracking, configuration item identification, change control, status accounting, configuration audits, storage/release, and joint-audit participation. Does not build the CM tooling itself.

**Announce at start:** "I'm using the config-management skill to record your NPR 7150.2D §5.1 configuration management compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A, B, C, and F carry all 8 rows below. Class D carries all of them except SWE-045 (§5.1.9, joint-audit participation), which does not apply to Class D. Class E carries none of these 8 rows — this skill has nothing to record for a Class E subsystem; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Configuration management plan (§5.1.2, SWE-079).** Where's the plan documenting who owns configuration management for this project — its functions, responsibilities, and authority?
2. **Change tracking (§5.1.3, SWE-080).** How are changes to software products tracked and evaluated?
3. **Configuration items (§5.1.4, SWE-081).** Which artifacts — code, data, tools, models, scripts, records — are under version control, and how are their versions identified? (Include build-affecting items like compiler/toolchain versions and environment settings, not just source code.)
4. **Change control procedures (§5.1.5, SWE-082).** What procedure defines the control levels each configuration item passes through, who is authorized to approve a change, and who is allowed to make changes at each level?
5. **Status records (§5.1.6, SWE-083).** Where are the configuration-status records for these items maintained?
6. **Configuration audits (§5.1.7, SWE-084).** How and when are configuration audits performed to confirm items match what's on record?
7. **Storage and release procedures (§5.1.8, SWE-085).** What's the procedure for storing, handling, delivering, releasing, and maintaining deliverable software products?
8. **Joint audit participation (§5.1.9, SWE-045).** Is there a plan for participating in any joint NASA/developer configuration audit, and who represents the project?

If any answer doesn't exist yet as a real artifact or process, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/config-management/scripts
python3 -c "
from record_config_management import record_config_management

record_config_management(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's config-management.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-079', 'SWE-080'>],
    fields={
        'cm_plan': '<answer to question 1>',
        'change_tracking': '<answer to question 2>',
        'configuration_items': '<answer to question 3>',
        'change_control_procedures': '<answer to question 4>',
        'status_records': '<answer to question 5>',
        'configuration_audits': '<answer to question 6>',
        'storage_release_procedures': '<answer to question 7>',
        'joint_audit_participation': '<answer to question 8>',
    },
    evidence='<the CM plan's path>',
)
print('Recorded.')
"
```

Only include the `fields` keys and matching `swe_ids` for questions the user actually answered with a real artifact this run — omit the rest rather than fabricating a value, and leave those rows `not-started`.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
