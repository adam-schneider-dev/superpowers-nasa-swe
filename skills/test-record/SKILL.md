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

1. **Test artifacts (§4.5.2, SWE-065).** Point to the four testing artifacts: the plan that lays out the overall test approach, the step-by-step procedures, the tests themselves (including any harness code written just to run them), and the report(s) summarizing outcomes.
2. **Requirements testing (§4.5.3, SWE-066).** Show the evidence tying test execution back to the requirements — how do you know every requirement got exercised by at least one test?
3. **Configuration management before test (§4.5.4, SWE-187).** Before testing began, was the exact version of the software under test placed under configuration management, so the test results are tied to a known, reproducible baseline?
4. **Test evaluation (§4.5.5, SWE-068).** After the tests ran, who looked at the results and judged pass/fail, and where's that judgment written down?
5. **Qualification tooling (§4.5.6, SWE-070).** If this subsystem is qualifying flight software or flight hardware, were the simulation/modeling/analysis tools used for that qualification themselves checked out and approved beforehand? If flight qualification isn't in scope here, say so.
6. **Plan/procedure currency (§4.5.7, SWE-071).** Have the test plan and procedures been kept in sync as the requirements changed, or could they be testing against an outdated version of what's required?
7. **Platform validation (§4.5.8, SWE-073).** Was this software actually run and validated on the real target hardware/platform, or on a simulation close enough to count? Point to that validation.
8. **Code coverage program (§4.5.9, SWE-189).** Walk through the code-coverage practice end to end: what coverage metric was picked, how is it collected, and where does the number get logged and reported?
9. **Code coverage verification (§4.5.10, SWE-190).** How do you confirm the coverage number is actually derived from real test runs, rather than an estimate or a stale figure?
10. **Regression testing (§4.5.11, SWE-191).** What's the regression-testing evidence that shows previously-working functionality is still working, and that nothing newly introduced opened up a security hole?
11. **Hazard-traced tests (§4.5.12, SWE-192).** For any requirement that exists because of a known hazard (its cause, or a mitigation for it), point to the test that actually exercises it. If nothing in scope here traces to a hazard, say so explicitly.
12. **Loaded/uplinked-data acceptance tests (§4.5.13, SWE-193).** If this software can be reconfigured after deployment by loading or uplinking new data, rules, or code that changes its behavior, point to the acceptance tests written for that update path. If there's no such path, say so.
13. **Reused-component testing (§4.5.14, SWE-211).** For any COTS, GOTS, MOTS, open-source, or otherwise reused piece embedded in this software, was it put through the same testing rigor you'd demand of a custom-built equivalent doing the same job? If nothing here is reused, say so.

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
