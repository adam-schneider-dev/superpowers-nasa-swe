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

## Catalog schema

Each row of `data/swe-catalog.yaml` mirrors one Appendix C row's structured columns (never its requirement text):

| Field | Appendix C column |
|---|---|
| `section` | Section |
| `swe_id` | SWE # |
| `class_ae_authority` | Class A-E Authority — who approves tailoring for Classes A-E (e.g. `Center`) |
| `classes` | the six per-class applicability columns; `true` where the source shows an `X` |
| `class_f_authority` | Class F Authority — who approves tailoring for Class F (`CIO`), `null` where Class F is not invoked, plus one documented exception: §3.2.1/`SWE-015` carries a Class F mark but names no authority in the source standard, so it too reads `null` (see `data/CATALOG-COVERAGE.md`) |

The two authority columns are distinct. Per NPR 7150.2D §2.1.5.4 the NASA CIO (or Center CIO designee) holds institutional authority on all Class F software projects, which is why `CIO` appears only alongside a Class F mark.

## Steps

1. Read the subsystem's `classification.yaml`, note its `class` field.
2. Read `<this plugin's install path>/data/swe-catalog.yaml`. The catalog covers all 100 Appendix C rows — no gap to disclose. Class E returns its real 12 rows.
3. Run — this validates the catalog before filtering it, so a corrupted or half-edited catalog fails loudly instead of quietly producing a short matrix:

```bash
cd <this-plugin's-install-path>/skills/requirements-matrix/scripts
python3 -c "
import sys
import yaml
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml
from validate_catalog import validate_catalog

with open('../../../data/swe-catalog.yaml') as f:
    catalog = yaml.safe_load(f)

errors = validate_catalog(catalog)
if errors:
    for e in errors:
        print('CATALOG ERROR:', e)
    sys.exit(1)

software_class = '<class from classification.yaml>'
subsystem = '<subsystem name>'

rows = filter_rows_for_class(catalog, software_class)
md = render_matrix_markdown(rows, subsystem, software_class)
status_rows = render_matrix_status_yaml(rows, software_class)

print(md)
print('---STATUS-YAML---')
print(yaml.dump(status_rows, sort_keys=False))
"
```

If the script exits with `CATALOG ERROR` lines, stop and report them — do not hand the user a matrix built from a catalog that failed validation.

4. Write the printed markdown to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.md` in the project being worked on.
5. Write the printed status YAML to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` in the same location. Each entry carries `swe_id`, `section`, `software_class`, `default_approver`, `status`, `evidence`, and `date`. `software_class` is the class this matrix was generated for — compare it against `classification.yaml`'s `class` to tell whether a matrix is still current or was left over from a previous class. `default_approver` is the authority resolved for this subsystem's class — the `class_f_authority` for Class F, the `class_ae_authority` otherwise — and it is what the `tailoring-request` skill offers as the default approving authority.
6. Tell the user how many requirements apply to their class and remind them the matrix only reflects the catalog's current coverage (per step 2).
7. Generate the parallel SA/safety task matrix (NASA-STD-8739.8B §4.3 Table 1) for whatever chapters `data/sa-task-catalog.yaml` currently covers — see `data/SA-TASK-CATALOG-COVERAGE.md` for its current scope:

```bash
cd <this-plugin's-install-path>/skills/requirements-matrix/scripts
python3 -c "
import yaml
from sa_task_matrix import filter_sa_task_rows_for_class, render_sa_task_matrix_markdown, render_sa_task_matrix_status_yaml

with open('../../../data/sa-task-catalog.yaml') as f:
    sa_task_catalog = yaml.safe_load(f)
with open('../../../data/swe-catalog.yaml') as f:
    swe_catalog = yaml.safe_load(f)

software_class = '<class from classification.yaml>'
subsystem = '<subsystem name>'

rows = filter_sa_task_rows_for_class(sa_task_catalog, swe_catalog, software_class)
if rows:
    md = render_sa_task_matrix_markdown(rows, subsystem, software_class)
    status_rows = render_sa_task_matrix_status_yaml(rows, software_class)
    print(md)
    print('---STATUS-YAML---')
    print(yaml.dump(status_rows, sort_keys=False))
else:
    print('NO SA TASK ROWS APPLICABLE — skip writing sa-task-mapping-matrix files')
"
```

If the script prints `NO SA TASK ROWS APPLICABLE`, do not write any SA task matrix files — this class has no applicable rows in the catalog's current coverage (either genuinely none, or the relevant chapter hasn't been added yet per `SA-TASK-CATALOG-COVERAGE.md`). Otherwise, write the printed markdown to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` — the same two-file pattern used for the main matrix. `sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence.
