---
name: ivv-verification-record
description: Use to record a subsystem's NASA-STD-8739.8B §4.4.2 IV&V provider verification evidence, once sa-ivv-coordination has confirmed IV&V applies
---

# IV&V Verification Requirements (NASA-STD-8739.8B §4.4.2)

## Overview

Records that the IV&V provider actually performed each of the 49 verification duties §4.4.2 assigns it, and where the evidence for each lives. Does not perform IV&V itself — that's real independent analysis and testing work this tool doesn't replace.

**Announce at start:** "I'm using the ivv-verification-record skill to record your NASA-STD-8739.8B §4.4.2 IV&V verification evidence."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml` to already exist. This file only exists once `sa-ivv-coordination` has recorded IV&V as applicable for this subsystem (§3.6.2/SWE-141) and generated it. If it's absent, either IV&V hasn't been engaged for this subsystem, or `sa-ivv-coordination` hasn't recorded that determination yet — check there first. Do not run this skill's script against a matrix that doesn't exist.

All 49 requirements apply uniformly once this file exists — there is no per-class filtering here, unlike the main SWE requirements matrix.

## The interview

Ask each group below in turn. For each, ask which of its listed ids have real, checkable evidence — an IV&V analysis artifact, a report reference, a tracked finding, an IPEP excerpt — and where that evidence lives. A vague "IV&V handled it" answer is not sufficient, same standard `peer-review-record` established: the evidence must point at something a human auditor could actually go check. If an id has no real evidence yet, leave it out of that group's `ivv_ids` below rather than recording an unverifiable claim.

1. **Planning & IPEP (4.4.2.1-3).** Has your Project SMA Technical Authority signed off on an IV&V Project Execution Plan (IPEP), and does that plan's scope actually trace back to a real risk assessment of which system/software behaviors need scrutiny — not just a boilerplate list?
2. **Reporting & review participation (4.4.2.4-8).** Walk through how visible IV&V's own work is to the rest of the project: what measurements does the IV&V side keep on itself, does it sit in on the project's own peer reviews, can the project actually monitor and audit IV&V's process and attend its technical interchange meetings, does IV&V show up at project milestone reviews with real status, and who ultimately receives its analysis conclusions and risk calls?
3. **Tracking & risk management (4.4.2.9-15).** Does the project actually close out the issues IV&V raises, not just receive them? Point to where IV&V's own defect/issue log lives, where a formal risk register captures what IV&V is tracking, whether IV&V has weighed in on whether the project's chosen life cycle fits the problem, whether it's confirmed the project is actually implementing the applicable NPR 7150.2 requirements, whether it's watching for risk when the software changes underneath it, and whether it's comparing actual progress against the plans.
4. **Concept, reuse & architecture basis (4.4.2.16-21).** Before the concept was locked in: were known security threats tracked and kept current as the design evolved, are known software-related hazard causes and their controls traced back to actual requirements, do the trade/feasibility studies genuinely support the decisions they were meant to inform, does the computing approach reflect what the mission actually needs operationally, does the architecture account for every computing element the mission requires, and — for anything planned for reuse — does it genuinely work as a drop-in replacement in the new application rather than just being close enough?
5. **Requirements verification (4.4.2.22-26).** Does the traceability between requirements and the architecture that implements them actually hold up? Do the requirements give the software the ability to control identified hazards without introducing new ones, do they carry the dependability and fault-tolerance properties the system needs, do they capture the mitigations for known security risks, and — independent of all that — do the requirements themselves read as consistent, complete, and correct on their own terms?
6. **Design verification (4.4.2.27-30).** Can you trace software requirements down into the detailed design components that implement them? Are the interfaces between those design components and everything they touch — hardware, users, other software, external systems — correct and complete? Is the detailed design itself testable, consistent, and traceable? And does the architecture actually meet the safety and mission-critical needs the requirements set out?
7. **Code & security verification (4.4.2.31-39).** Starting from the code itself: can you trace it back to the requirements it implements and down to the design units it comes from? Has the source code actually been run through analysis tooling — static, dynamic, or otherwise? Have the required security mitigations actually been implemented, and was a real vulnerability assessment done first? For any off-the-shelf or open-source components, have their security risks been identified and handled? Are security risks in the custom code itself identified and mitigated? Does the code follow your coding standards? And, stepping back, is the code and its data consistent with the architecture and complete against the requirements?
8. **Test verification (4.4.2.40-47).** For anything loaded or uplinked after launch — data, rules, code — are there real acceptance tests for it? Are the requirements that trace to a hazard cause or mitigation independently tested, not just covered incidentally? Is code coverage actually measured from test execution, and are the required security mitigations tested? Do the test results actually meet their acceptance criteria, and are those criteria objective ones covering both nominal and off-nominal conditions? Can you trace the tests back to the code and system functions they're supposed to verify? And are the test plans, cases, procedures, and environment themselves correct, complete, and consistent across all levels of testing?
9. **Maintenance & audit participation (4.4.2.48-49).** Has IV&V assessed the risks around software maintenance and operations to plan its own activities during that phase, and does it participate in NASA's quality audits, assessments, and reviews for the project?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/ivv-verification-record/scripts
python3 -c "
from record_ivv_verification import record_ivv_verification

record_ivv_verification(
    matrix_yaml_path='<path to the subsystem's ivv-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's ivv-verification-record.md>',
    ivv_ids=[<ids answered above with checkable evidence, e.g. 'IVV-4.4.2.1', 'IVV-4.4.2.2', 'IVV-4.4.2.3'>],
    fields={
        'planning_and_ipep': '<answer to question 1>',
        'reporting_and_reviews': '<answer to question 2>',
        'tracking_and_risk': '<answer to question 3>',
        'concept_reuse_and_architecture': '<answer to question 4>',
        'requirements_verification': '<answer to question 5>',
        'design_verification': '<answer to question 6>',
        'code_and_security_verification': '<answer to question 7>',
        'test_verification': '<answer to question 8>',
        'maintenance_and_audits': '<answer to question 9>',
    },
    evidence='<the primary evidence artifact's path or reference>',
)
print('Recorded.')
"
```

Only pass ids that actually have checkable evidence for the fields you're filling in this run — you don't need to answer all 9 groups in one pass. Run the script again later as more evidence becomes available; each run appends a new `## Recorded` entry.

## Writing the output

Confirm to the user which ids were marked satisfied and where the record was written.
