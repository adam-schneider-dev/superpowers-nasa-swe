# SWE Catalog Coverage

`data/swe-catalog.yaml` currently covers NPR 7150.2D Appendix C, pages 70-78:

- 4.2 Software Architecture
- 4.3 Software Design
- 4.4 Software Implementation
- 4.5 Software Testing
- 4.6 Software Operations, Maintenance, and Retirement
- 5.1 Software Configuration Management
- 5.2 Software Risk Management
- 5.3 Software Peer Reviews/Inspections
- 5.4 Software Measurements
- 5.5 Software Non-conformance or Defect Management

**Not yet covered** (tracked here, not silently missing):

- Chapter 2 (Roles/Responsibilities) — excluded permanently: NPR 7150.2D §1.3.1 states Chapter 2 requirements are not part of the Requirements Mapping Matrix.
- Chapter 3 (Software Management Requirements, §3.1-3.12) and the start of §4.1 (Software Requirements) — Appendix C pages preceding page 70. Needs a follow-up transcription pass before `requirements-matrix` results are complete for any subsystem that needs Chapter 3 rows.

Extending coverage: re-run the transcription method from Task 6 of `docs/superpowers/plans/2026-08-10-nasa-swe-foundation.md` against the missing page range, append rows to `swe-catalog.yaml`, re-run `validate_catalog`, and update this file.
