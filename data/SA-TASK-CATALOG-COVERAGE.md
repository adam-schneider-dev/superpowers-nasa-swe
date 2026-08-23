# SA Task Catalog Coverage

**`data/sa-task-catalog.yaml` covers 82 of NASA-STD-8739.8B §4.3 Table 1's 103 rows.**

Table 1 splits cleanly along NPR 7150.2D's own chapter boundaries — the same
ones SP2/SP3/SP4 used to build `data/swe-catalog.yaml` and its 13 record
skills. This catalog is being built the same way, one chapter at a time.

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

## Not yet covered

- **Chapter 5, Supporting Lifecycle, 21 rows** — SP5 Part 2c, not started.

`requirements-matrix`'s `sa-task-mapping-matrix.yaml` output reflects
whatever this catalog currently covers — a subsystem generated before Part
2c lands gets a Chapter 3+4-only SA-task matrix. Re-running `requirements-matrix`
after it lands picks up the newly added rows.

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
