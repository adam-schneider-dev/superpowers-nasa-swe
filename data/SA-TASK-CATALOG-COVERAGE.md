# SA Task Catalog Coverage

**`data/sa-task-catalog.yaml` covers all 103 of NASA-STD-8739.8B §4.3 Table 1's rows.**

Table 1 splits cleanly along NPR 7150.2D's own chapter boundaries — the same
ones SP2/SP3/SP4 used to build `data/swe-catalog.yaml` and its 13 record
skills. This catalog was built the same way, one chapter at a time.

## Covered — Chapter 3, Software Management, 45 rows (SP5 Part 2a)

- 3.1 Software Life Cycle Planning
- 3.2 Software Cost Estimation
- 3.3 Software Schedules
- 3.4 Software Training
- 3.5 Software Classification Assessments
- 3.6 Software Assurance and Software Independent Verification & Validation
- 3.7 Safety-Critical and Mission-Critical Software
- 3.8 Automatic Generation of Software Source Code
- 3.9 Software Development Processes and Practices
- 3.10 Software Reuse
- 3.11 Software Cybersecurity
- 3.12 Software Bi-Directional Traceability

## Covered — Chapter 4, Software Engineering, 37 rows (SP5 Part 2b)

- 4.1 Software Requirements
- 4.2 Software Architecture
- 4.3 Software Design
- 4.4 Software Implementation
- 4.5 Software Testing
- 4.6 Software Operations, Maintenance, and Retirement

Note: SWE-065's four lettered sub-tasks (065a-065d, all under NPR section
4.5.2) share a single row in `data/swe-catalog.yaml` (`SWE-065`). Class
applicability for all four is looked up against that one shared row —
`sa_task_matrix.py` strips a trailing letter suffix before the lookup.

## Covered — Chapter 5, Supporting Software Life Cycle, 21 rows (SP5 Part 2c)

- 5.1 Software Configuration Management
- 5.2 Software Risk Management
- 5.3 Software Peer Reviews/Inspections
- 5.4 Software Measurements
- 5.5 Software Non-conformance or Defect

Table 1 ends at §5.5.4 / SWE-204 — it has no Chapter 6 or 7 rows. With Chapter
5 added, this catalog covers the table in full.

Note: Class E has no applicable Chapter 5 rows at all. Per-class applicable
counts, inherited from `swe-catalog.yaml`: A 21, B 21, C 19, D 8, E 0, F 13.

A subsystem whose `sa-task-mapping-matrix.yaml` was generated before this
chapter landed carries only Chapter 3-4 rows; re-running `requirements-matrix`
regenerates it against the full catalog.

## Verifying coverage

```bash
python3 -c "
import yaml
with open('data/sa-task-catalog.yaml') as f:
    rows = yaml.safe_load(f)
print(len(rows), 'rows')
print(sorted({r['section'].split('.')[0] for r in rows}))
"
```
