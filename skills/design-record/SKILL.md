---
name: design-record
description: Use to record a subsystem's NPR 7150.2D §4.3 software design, based on its architecture, down to codeable/testable units
---

# Software Design (NPR 7150.2D §4.3)

## Overview

Records the software design description — based on the architecture, describing lower-level units so they can be coded, compiled, and tested. Does not author the design itself.

**Announce at start:** "I'm using the design-record skill to record your NPR 7150.2D §4.3 software design compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Design description (§4.3.2, SWE-058).** Where's the design that breaks the architecture down further — to the level of individual units a developer could actually sit down and code, compile, and test? If that document doesn't exist yet, say so rather than pointing at the architecture doc again.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/design-record/scripts
python3 -c "
from record_design_record import record_design_record

record_design_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's design-record.md>',
    swe_ids=['SWE-058'],
    fields={'design_description': '<answer to question 1>'},
    evidence='<the design document's path>',
)
print('Recorded.')
"
```

If no design document exists yet, don't run the script — tell the user the row stays `not-started` until one exists.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
