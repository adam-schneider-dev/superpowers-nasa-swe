---
name: cybersecurity-assessment
description: Use to record a subsystem's NPR 7150.2D §3.11 software cybersecurity risk categorization and control basis, citing the project's existing ATO/RMF artifact rather than performing RMF itself
---

# Software Cybersecurity Assessment (NPR 7150.2D §3.11)

## Overview

Records the software cybersecurity assessment and risk/mitigation identification §3.11 requires. **Does not perform RMF categorization itself** — cites the project's existing Authority to Operate (ATO) or RMF artifact. Performing an actual RMF categorization is real security engineering work this tool doesn't replace.

**Announce at start:** "I'm using the cybersecurity-assessment skill to record your NPR 7150.2D §3.11 cybersecurity assessment."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Cybersecurity assessment (§3.11.2, SWE-156).** Point to the existing assessment covering the software components per Agency security policy and project requirements — including risks from any COTS, GOTS, MOTS, OSS, or reused components. If none exists yet, say so and stop rather than fabricating a categorization.
2. **Risk identification and mitigation (§3.11.3, SWE-154).** What cybersecurity risks were identified for this software (flight or ground), and what mitigations are planned/in place?
3. **Reused-component risk (ties to `reuse-assessment`).** If this subsystem has any reuse-assessment records, note whether their license/POC review surfaced any cybersecurity-relevant findings.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/cybersecurity-assessment/scripts
python3 -c "
from record_cybersecurity_assessment import record_cybersecurity_assessment

record_cybersecurity_assessment(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's cybersecurity-assessment.md>',
    swe_ids=['SWE-156', 'SWE-154'],
    fields={
        'risk_categorization': '<answer to question 1>',
        'control_basis': '<pointer to the ATO/RMF artifact>',
        'cots_reused_component_risks': '<answer to question 3, or "none identified">',
    },
    evidence='<the ATO/RMF artifact's path>',
)
print('Recorded.')
"
```

If there's no ATO/RMF artifact to cite yet, don't run the script — tell the user the rows stay `not-started` until one exists.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
