---
name: measurements
description: Use to record a subsystem's NPR 7150.2D §5.4 software measurement program
---

# Software Measurements (NPR 7150.2D §5.4)

## Overview

Records what software measures/metrics this project collects, how they're analyzed, who can access them, and how they're used to track performance and requirements volatility. Does not collect or analyze the measurements itself.

**Announce at start:** "I'm using the measurements skill to record your NPR 7150.2D §5.4 measurement compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A and B carry all 5 rows below. Class C carries all but SWE-200 (§5.4.6, requirements volatility), which applies only to Classes A and B. Classes D, E, and F carry none of these 5 rows — this skill has nothing to record for those subsystems; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Measurement program (§5.4.2, SWE-090).** Which numbers does this project keep on its software — the ones a manager watches and the ones an engineer watches? Point me at where they live, whose job it is to keep them current, who sees them, and one decision that actually came out differently because of them.
2. **Analysis procedure (§5.4.3, SWE-093).** What documented procedure is used to analyze the collected measurement data?
3. **Data access (§5.4.4, SWE-094).** When an oversight body outside the project asks — your sponsoring Mission Directorate, the NASA Chief Engineer, a Center Technical Authority, HQ SMA, or similar — what mechanism actually hands over the numbers, whatever you've concluded from them, and a current read on where development stands? Name the mechanism, not the willingness.
4. **Performance monitoring (§5.4.5, SWE-199).** What's actually being measured to give you confidence the software will land within its performance budget, do what it's supposed to do, and stay inside its stated constraints?
5. **Requirements volatility (§5.4.6, SWE-200).** Requirements churn over a project's life. Does this project put a number on that churn, and where does that number end up — who reads it, and how often?

If any answer doesn't exist yet as a real artifact or process, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/measurements/scripts
python3 -c "
from record_measurements import record_measurements

record_measurements(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's measurements.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-090', 'SWE-093'>],
    fields={
        'measurement_program': '<answer to question 1>',
        'analysis_procedure': '<answer to question 2>',
        'data_access': '<answer to question 3>',
        'performance_monitoring': '<answer to question 4>',
        'requirements_volatility': '<answer to question 5>',
    },
    evidence='<the measurement plan's path>',
)
print('Recorded.')
"
```

Only include the `fields` keys and matching `swe_ids` for questions the user actually answered with a real artifact this run — omit the rest rather than fabricating a value, and leave those rows `not-started`.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
