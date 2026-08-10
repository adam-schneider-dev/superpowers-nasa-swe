---
name: classify-software
description: Use when starting a new project or subsystem that needs a NASA-wide software classification (NPR 7150.2D Appendix D, Class A-F) before other NASA-SWE compliance skills can run
---

# Classify Software (NPR 7150.2D Appendix D)

## Overview

Determines which NASA software class (A-F) applies to a project or named subsystem, using NPR 7150.2D Appendix D's actual class definitions. This must run before `requirements-matrix`, since the matrix is filtered by class.

**Announce at start:** "I'm using the classify-software skill to determine your NASA software class per NPR 7150.2D Appendix D."

## Multiple subsystems

Ask first: is this a single system, or does the project contain subsystems that might warrant different classes (NPR 7150.2D Appendix D.1 explicitly anticipates this)? If subsystems exist, run this interview once per named subsystem, producing one `classification.yaml` per subsystem.

## The interview

Ask about each class in order, using the criteria below — **paraphrased and condensed from Appendix D, not verbatim**. Consult `<this plugin's install path>/reference/NPR_7150.2D.pdf`, Appendix D, for the authoritative wording, and do so before recording any classification a user intends to rely on or defend. Where a paraphrase below and the PDF disagree, the PDF governs.

The first "yes" determines the class — but keep asking through Class E even after an earlier "yes", so the tool can detect and flag ambiguity (more than one class's criteria matching is a real signal, not noise).

1. **Class A — Human Rated Space Software Systems.** Does the software: operate a vehicle/space asset including commanding it, OR sustain a safe habitable environment for crew, OR directly achieve primary human-spaceflight mission objectives, OR directly prepare resources (data/fuel/power) consumed by those functions? Exclude software that's merely incidental to the mission (e.g., personal media on a crew device), aeronautics-only R&T software with no space-flight application, and simulator/test-environment software.

2. **Class B — Non-Human Space Rated Systems or Large-Scale Aeronautics.** For non-human space missions: does the software operate the vehicle/asset (commanding), achieve primary mission objectives, or directly prepare consumed resources? OR, for large-scale (>$250M lifecycle cost per NPR 7120.8) NASA-unique aeronautic vehicles: is the software integral to airborne vehicle control, or does it monitor/control the cabin environment or the vehicle's emergency systems? Exclude software solely supporting non-primary instruments, and simulator/test-environment software.

3. **Class C — Mission Support Software, Aeronautic Vehicles, or Major Engineering/Research Facility Software.** Any of: software for a single non-primary instrument's science return; software analyzing/processing mission data; software whose defect could affect secondary mission objectives or cause operational problems; software testing space assets or verifying system requirements by analysis; space flight ops software not covered by A/B; non-large-scale aeronautic vehicle software integral to control/cabin/emergency systems, or that records the official flight/test data; major engineering/research facility control, monitoring, or data-acquisition software; sounding rocket/payload software; NASA Class D payload software (NPR 8705.4).

4. **Class D — Basic Science/Engineering Design and Research and Technology Software.** Any of: secondary science data analysis tools; engineering development tools; informal software testing tools; mission planning/formulation tools; decision support for non-mission-critical situations; research/development/test/evaluation lab software (not a major facility); airborne-vehicle software with only a minor or no-effect failure condition (DO-178C Class D/E equivalent); research software independent of a major facility's operation.

5. **Class E — Design Concept, Research, Technology, and General Purpose Software.** Software exploring a design concept/hypothesis not used to make decisions for an operational A/B/C system; minor analyses of science/experimental data; a defect would affect at most a single user or small group, not mission objectives or system safety; runs in a general-purpose computing or board-top environment, not used for ground/flight tests or operations.

6. **Safety-critical check (always ask, regardless of the above).** Per NASA-STD-8739.8B §4.2.1, is the software determined by and traceable to a hazard analysis to: cause/contribute to a system hazardous condition, control functions identified in a system hazard, mitigate a hazardous condition, mitigate damage if a hazard occurs, or detect/report/correct a hazardous state? If yes, `is_safety_critical: true` — this can never leave the result at Class E; Class E software cannot be safety-critical.

If none of Classes A-E apply, the software is **Class F** — general-purpose computing, business, and IT software.

## Running the script

Translate your interview answers into the exact keys `classify.py` expects, then run it:

```bash
cd <this-plugin's-install-path>/skills/classify-software/scripts
python3 -c "
from classify import classify
import json
result = classify({
    'class_a_human_rated': False,
    'class_b_non_human_space_or_large_aero': False,
    'class_c_mission_support_or_facility': False,
    'class_d_basic_science_or_research': False,
    'class_e_design_concept_general_purpose': True,
    'is_safety_critical': False,
})
print(json.dumps(result, indent=2))
"
```

If `result["ambiguous"]` is `true`, **do not silently accept the first candidate** — tell the user which classes matched (`result["candidates"]`) and ask them to confirm or override, per NPR 7150.2D Appendix D.2.

## Writing the output

Write `docs/nasa-compliance/<subsystem>/classification.yaml` in the *project being classified* (create the directory if needed):

```yaml
subsystem: <name, or "default" for a single-system project>
class: <A-F from the script result>
ambiguous: <bool from the script result>
candidates: <list from the script result>
answers: <the exact answers dict passed to classify()>
rationale: <one paragraph, in your own words, explaining why this class fits, citing the specific Appendix D criteria that matched>
date: <today's date, YYYY-MM-DD>
```
