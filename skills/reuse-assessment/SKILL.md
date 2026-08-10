---
name: reuse-assessment
description: Use to record software reuse assessments per NPR 7150.2D — both this project's own contribution to NASA's reuse system (§3.10) and the suitability conditions for each incoming COTS/GOTS/MOTS/OSS or reused component (§3.1.14)
---

# Software Reuse Assessment (NPR 7150.2D §3.10, §3.1.14)

## Overview

Covers the two directions of software reuse, which are different requirements and are recorded separately:

- **Part 1 — outbound (§3.10.1/SWE-147, §3.10.2/SWE-148):** does this project's own software specify reusability requirements, and is the information NASA's reuse system needs recorded for the software being contributed?
- **Part 2 — incoming (§3.1.14/SWE-027):** are the conditions for acquiring or using a COTS, GOTS, MOTS, OSS, or reused software component satisfied for each such component?

Run each part once per component being recorded — every run appends its own entry to the record file.

**Announce at start:** "I'm using the reuse-assessment skill to record a software reuse assessment."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## Part 1: Contributing this project's software for reuse (§3.10)

Per SWE-148, record at minimum:

1. **Software title and description** — what is the component, and what does it do in this project?
2. **Technical POC** — who is the civil servant technical point of contact for this software product?
3. **Language(s)** — what language(s) was it developed in?
4. **Third-party licensing** — any third-party code within it, and the license/permission record for NASA's use, including required copyright/author/license notices and the source URL(s) if applicable.
5. **Release notes** — a pointer to them, if the component has its own release notes.
6. **Reusability of this project's own output (§3.10.1, SWE-147)** — does this project's own software specify reusability requirements so it, in turn, can be reused by others?

### Running the script (Part 1)

If the subsystem's class has no rows for this section in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check before running: Appendix C does not invoke `SWE-147` (§3.10.1) on Class E, so a Class E subsystem records `SWE-148` alone.

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

Repeat for each additional component being contributed.

## Part 2: Using an incoming reused/COTS/GOTS/MOTS/OSS component (§3.1.14)

§3.1.14 (SWE-027) sets conditions the project manager must satisfy when such a component is **acquired or used** — this is about bringing software *in*, not contributing software *out*, so it is a separate assessment from Part 1 even when it concerns the same component. Run it once per incoming component.

Walk all six conditions and record the answer to each:

a. **Requirements identified** — which of this project's requirements is the component meant to meet? Name them.
b. **Documentation** — does the component ship documentation sufficient for its intended purpose (e.g. usage instructions)? Point to it.
c. **Proprietary and usage rights** — have proprietary rights, usage rights, ownership, warranty, licensing rights, transfer rights, and conditions of use been addressed **and coordinated with Center Intellectual Property Counsel**? Record the coordination, not just the license name. If that coordination hasn't happened, say so and stop — do not record it as satisfied.
d. **Future support** — is future support for the product planned and adequate for the project's needs (vendor roadmap, LTS window, internal fork/mirror, or an explicit end-of-support plan)?
e. **Verification and validation** — is the component verified and validated to the same level required to accept a similar developed component for its intended use? Say what that level is and where the evidence lives.
f. **Vendor defect assessments** — what is the plan for periodically assessing vendor-reported defects to confirm they don't affect the selected component (e.g. a scheduled review of the vendor's defect/CVE feed)?

If any condition has no real answer yet, tell the user it is an open gap and don't run the script — a `SWE-027` row marked satisfied asserts all six conditions were met.

### Running the script (Part 2)

If the subsystem's class has no rows for this section in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Appendix C does not invoke `SWE-027` on Class E.

```bash
cd <this-plugin's-install-path>/skills/reuse-assessment/scripts
python3 -c "
from record_reuse_assessment import record_reuse_assessment

record_reuse_assessment(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's reuse-assessment.md>',
    swe_ids=['SWE-027'],
    fields={
        'component_name': '<the incoming component being assessed>',
        'requirements_identified': '<answer to condition a>',
        'documentation': '<answer to condition b>',
        'ip_rights_coordination': '<answer to condition c, naming the Center IP Counsel coordination>',
        'future_support_plan': '<answer to condition d>',
        'verification_validation_level': '<answer to condition e>',
        'vendor_defect_assessment_plan': '<answer to condition f>',
    },
    evidence='<pointer to the suitability assessment record>',
)
print('Recorded.')
"
```

Repeat for each additional incoming component.

## Writing the output

Confirm to the user which component was recorded, under which part, and where. Note that a SWE-id gets marked satisfied on the first successful assessment that names it — the record file itself lists every component assessed since, so a later reviewer sees the full history, not just the latest.

If the script raises `ValueError` about a row being `tailored-out`, stop: an approved tailoring already relieved that row (see `tailoring-log.md`), and marking it satisfied would silently contradict that decision.
