---
name: peer-review-record
description: Use to record a subsystem's NPR 7150.2D §5.3 software peer review/inspection evidence
---

# Software Peer Reviews/Inspections (NPR 7150.2D §5.3)

## Overview

Records that a required peer review or inspection actually happened and where its results were reported. Does not conduct the review itself — for reviewing code changes, use this repo's existing `requesting-code-review`/`receiving-code-review` skills (or an equivalent external review process) first, then come back here to record it.

**Announce at start:** "I'm using the peer-review-record skill to record your NPR 7150.2D §5.3 peer review/inspection compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A, B, and C carry all 3 rows below. Class F carries SWE-087 and SWE-089 but not SWE-088. Classes D and E carry none of these 3 rows — this skill has nothing to record for those subsystems; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Reviews performed (§5.3.2, SWE-087).** Peer review/inspection coverage can span several kinds of artifact: the code that's actually shipped, the test procedures written to exercise it, any design items your plans flagged for review, and the upstream material driving all of it — what the system's supposed to do, and how the team (cybersecurity included) plans to build it. Which of those has actually had a peer review or inspection completed, and where was each one reported?
2. **Review procedure (§5.3.3, SWE-088).** When your team actually sits down for one of these reviews — what method guides how you evaluate the material (a checklist, a structured reading approach, something else), how do you know it's ready to review and when it's actually done, who has to be in the room, and what happens to the issues that come out of it until they're closed?
3. **Review measurements (§5.3.4, SWE-089).** What data comes out of a review that this project keeps — defect counts, time spent, who took part, anything else — and where does it get written down?

**Evidence must be checkable, not a self-attestation.** A vague "we reviewed it" answer is not sufficient — the evidence you record must point at something a human auditor could actually go look at: a specific PR URL, a `requesting-code-review`/`receiving-code-review` transcript reference, or an equivalent record from an external review process. If the user can't point to something concrete, tell them and leave the row `not-started` rather than recording an unverifiable claim.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/peer-review-record/scripts
python3 -c "
from record_peer_review_record import record_peer_review_record

record_peer_review_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's peer-review-record.md>',
    swe_ids=[<SWE-ids answered above with checkable evidence, e.g. 'SWE-087', 'SWE-088', 'SWE-089'>],
    fields={
        'reviews_performed': '<answer to question 1>',
        'review_procedure': '<answer to question 2>',
        'review_measurements': '<answer to question 3>',
    },
    evidence='<the specific PR URL or review record reference>',
)
print('Recorded.')
"
```

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
