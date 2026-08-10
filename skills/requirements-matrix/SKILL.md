---
name: requirements-matrix
description: Use after classify-software has produced a classification.yaml, to generate the project's NPR 7150.2D Requirements Mapping Matrix scoped to its declared software class
---

# Requirements Mapping Matrix (NPR 7150.2D Appendix C)

## Overview

Filters the bundled SWE requirement catalog to the subsystem's declared class and writes both a human-readable matrix and a machine-readable status file that later NASA-SWE skills update as compliance work proceeds.

**Announce at start:** "I'm using the requirements-matrix skill to generate your NPR 7150.2D Requirements Mapping Matrix."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/classification.yaml` to already exist (produced by the `classify-software` skill). If it doesn't exist, stop and run that skill first.

## Steps

1. Read the subsystem's `classification.yaml`, note its `class` field.
2. Read `<this plugin's install path>/data/swe-catalog.yaml`. Check `<this plugin's install path>/data/CATALOG-COVERAGE.md` and tell the user which NPR sections are and are not yet represented in the catalog — an incomplete catalog means an incomplete matrix, and the user needs to know that up front, not discover it later.
3. Run:

```bash
cd <this-plugin's-install-path>/skills/requirements-matrix/scripts
python3 -c "
import yaml
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml

with open('../../../data/swe-catalog.yaml') as f:
    catalog = yaml.safe_load(f)

software_class = '<class from classification.yaml>'
subsystem = '<subsystem name>'

rows = filter_rows_for_class(catalog, software_class)
md = render_matrix_markdown(rows, subsystem, software_class)
status_rows = render_matrix_status_yaml(rows)

print(md)
print('---STATUS-YAML---')
print(yaml.dump(status_rows, sort_keys=False))
"
```

4. Write the printed markdown to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.md` in the project being worked on.
5. Write the printed status YAML to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` in the same location.
6. Tell the user how many requirements apply to their class and remind them the matrix only reflects the catalog's current coverage (per step 2).
