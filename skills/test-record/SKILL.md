---
name: test-record
description: Use to record a subsystem's NPR 7150.2D §4.5 software testing evidence — test artifacts, requirements-based testing, coverage, regression, and reused-component testing
---

# Software Testing (NPR 7150.2D §4.5)

## Overview

Records the testing-phase evidence §4.5 requires across its 13 rows: test plans/procedures/reports, requirements-based testing, configuration management before test, evaluation, qualification tooling, platform validation, code coverage, regression testing, hazard-traced tests, loaded/uplinked-data acceptance tests, and reused-component testing. Does not run the tests itself — this is a real, larger interview than SP2's skills, but the same straight per-row walk applies; there is no special-casing for its row count.

**Announce at start:** "I'm using the test-record skill to record your NPR 7150.2D §4.5 software testing compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Test artifacts (§4.5.2, SWE-065).** Point to the software test plan(s), test procedure(s), test(s) — including any code written specifically to perform test procedures — and test report(s).
2. **Requirements testing (§4.5.3, SWE-066).** Point to evidence the software was tested against its requirements.
3. **Configuration management before test (§4.5.4, SWE-187).** Were software items placed under configuration management prior to testing?
4. **Test evaluation (§4.5.5, SWE-068).** Point to the recorded evaluation of test results.
5. **Qualification tooling (§4.5.6, SWE-070).** If this subsystem involves flight software or flight equipment qualification, were validated and accredited models, simulations, and analysis tools used? If not applicable, record that explicitly.
6. **Plan/procedure currency (§4.5.7, SWE-071).** Were the test and verification plan(s)/procedure(s) updated to stay consistent with the current software requirements?
7. **Platform validation (§4.5.8, SWE-073).** Point to evidence the software system was validated on the targeted platform or a high-fidelity simulation.
8. **Code coverage program (§4.5.9, SWE-189).** How are code coverage measurements selected, implemented, tracked, recorded, and reported?
9. **Code coverage verification (§4.5.10, SWE-190).** How is code coverage verified by analysis of the results of test execution?
10. **Regression testing (§4.5.11, SWE-191).** Point to the regression testing plan/results demonstrating that defects have not been introduced into previously integrated/tested software and no security vulnerability was produced.
11. **Hazard-traced tests (§4.5.12, SWE-192).** Point to test evidence for any software requirements that trace to a hazardous event, cause, or mitigation technique. If none trace to a hazard, record that explicitly.
12. **Loaded/uplinked-data acceptance tests (§4.5.13, SWE-193).** If the software accepts loaded or uplinked data, rules, or code that affects software/system behavior, point to the acceptance tests developed for it. If not applicable, record that explicitly.
13. **Reused-component testing (§4.5.14, SWE-211).** If embedded COTS/GOTS/MOTS/OSS/reused components exist, were they tested to the same level required to accept a custom-developed component for its intended use? If there are none, record that explicitly.

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below. Where a row genuinely doesn't apply (e.g. no reused components, no hazard-traced requirements), still record the explicit non-applicability determination rather than leaving the row silently `not-started`.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/test-record/scripts
python3 -c "
from record_test_record import record_test_record

record_test_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's test-record.md>',
    swe_ids=[<SWE-ids answered above, e.g. 'SWE-065', 'SWE-066', 'SWE-187', 'SWE-068', 'SWE-070', 'SWE-071', 'SWE-073', 'SWE-189', 'SWE-190', 'SWE-191', 'SWE-192', 'SWE-193', 'SWE-211'>],
    fields={
        'test_artifacts': '<answer to question 1>',
        'requirements_testing': '<answer to question 2>',
        'configuration_management_before_test': '<answer to question 3>',
        'test_evaluation': '<answer to question 4>',
        'qualification_tooling': '<answer to question 5>',
        'plan_procedure_currency': '<answer to question 6>',
        'platform_validation': '<answer to question 7>',
        'code_coverage_program': '<answer to question 8>',
        'code_coverage_verification': '<answer to question 9>',
        'regression_testing': '<answer to question 10>',
        'hazard_traced_tests': '<answer to question 11>',
        'loaded_uplinked_data_tests': '<answer to question 12>',
        'reused_component_testing': '<answer to question 13>',
    },
    evidence='<the single most authoritative pointer among the answers above, e.g. the test plan path>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer (including an explicit non-applicability determination).

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
