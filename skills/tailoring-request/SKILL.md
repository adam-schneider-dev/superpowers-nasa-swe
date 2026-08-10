---
name: tailoring-request
description: Use when a requirement in the project's requirements-mapping-matrix.yaml cannot be fully implemented, to record a NASA-style tailoring/request-for-relief entry with rationale, risk, mitigation, and approving authority
---

# Tailoring / Request for Relief

## Overview

Implements the tailoring principles from NPR 7150.2D Chapter 2 and NASA-STD-8739.8B §4.5: a requirement that isn't fully implemented must have a documented, approved rationale — never a silent gap.

**Announce at start:** "I'm using the tailoring-request skill to record a tailoring/relief entry."

## Steps

1. Ask which SWE-id (from the subsystem's `requirements-mapping-matrix.yaml`) is being tailored, and confirm it's actually present in that file — if you're not sure, look it up rather than guessing the id.
2. Ask for, in the user's own words: rationale (why this doesn't apply or can't be met as written), risk (what could go wrong if this is skipped), mitigation (what reduces that risk), and approver (a named person or role — the matrix row's `technical_authority` field is the default suggestion, from `filter_matrix.py`'s output, but the user may name someone else).
3. If the user has no approver to name, stop — do not record an entry without one. Explain that NPR 7150.2D 2.1.5.4's note requires tailoring to be approved and recorded with rationale, not simply asserted.
4. Run:

```bash
cd <this-plugin's-install-path>/skills/tailoring-request/scripts
python3 -c "
from add_tailoring_entry import add_tailoring_entry

add_tailoring_entry(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    log_md_path='<path to the subsystem's tailoring-log.md>',
    swe_id='<SWE-id>',
    rationale='<rationale>',
    risk='<risk>',
    mitigation='<mitigation>',
    approver='<approver>',
)
print('Recorded.')
"
```

5. Confirm to the user which SWE-id was tailored and where the log entry was written.
