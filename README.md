# Superpowers: NASA-SWE

Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them.

**This is a fork of [obra/superpowers](https://github.com/obra/superpowers) that adds a NASA software engineering compliance layer.** Upstream's 14 skills are unchanged and still drive the day-to-day work. Alongside them, this fork ships 24 more skills that classify your project under NPR 7150.2D, generate the requirements matrix scoped to that class, and then interview your team to record the compliance evidence NPR 7150.2D and NASA-STD-8739.8B ask for.

**The compliance skills record evidence — they don't do the engineering.** `cost-estimation` doesn't compute an estimate, `measurements` doesn't collect metrics, `cybersecurity-assessment` doesn't run RMF, `peer-review-record` doesn't conduct the review, `ivv-verification-record` doesn't perform IV&V. Each one asks your human partner what happened and where the artifact lives, then writes a structured record of it.

## The compliance layer

### Start here

| Skill | What it does |
| --- | --- |
| `classify-software` | Determines a project or subsystem's NASA software class (A–F) per NPR 7150.2D Appendix D. Everything else depends on its `classification.yaml`. |
| `requirements-matrix` | Generates the project's Requirements Mapping Matrix, scoped to the declared class, from the bundled Appendix C catalog. Also generates the SA task matrix the assurance skills read. |
| `safety-critical-determination` | Runs the full NPR 7150.2D §3.7 / NASA-STD-8739.8B §4.2 safety-critical determination and reconciles it back into `classification.yaml`. |
| `tailoring-request` | Records a NASA-style tailoring / request-for-relief entry — rationale, risk, mitigation, approving authority — for any matrix requirement that can't be fully implemented. |

### Recording NPR 7150.2D compliance

One skill per section of the NPR, each walking the matrix rows that apply to your class.

**Chapter 3 — Software Management**

| Skill | Section |
| --- | --- |
| `lifecycle-planning` | §3.1 — acquisition vs. development, plans, milestones, acceptance criteria |
| `cost-estimation` | §3.2 — methodology, basis of estimate, size/effort parameters |
| `sa-ivv-coordination` | §3.6 — software assurance, software safety, and IV&V roles and plan |
| `reuse-assessment` | §3.10 outbound (contributing your software to NASA's reuse system) and §3.1.14 inbound (suitability conditions per COTS/GOTS/MOTS/OSS component) |
| `cybersecurity-assessment` | §3.11 — cybersecurity risk categorization, citing your existing ATO/RMF artifact |
| `traceability` | §3.12 — the bi-directional traceability mechanism and where it lives |

**Chapter 4 — Software Engineering**

| Skill | Section |
| --- | --- |
| `requirements-definition` | §4.1 — definition, analysis, safety constraints, change tracking, validation |
| `architecture-record` | §4.2 — architecture description and, where applicable, its review |
| `design-record` | §4.3 — design down to codeable/testable units |
| `implementation-record` | §4.4 — coding standards, static analysis, unit testing, version description, tool validation |
| `test-record` | §4.5 — testing evidence across its 13 matrix rows |
| `operations-retirement` | §4.6 — operations, maintenance, and retirement planning and evidence |

**Chapter 5 — Supporting Lifecycle**

| Skill | Section |
| --- | --- |
| `config-management` | §5.1 — configuration management plan, mechanisms, evidence |
| `risk-management` | §5.2 — software risk management process |
| `peer-review-record` | §5.3 — peer review/inspection evidence (record it here after running `requesting-code-review`/`receiving-code-review` or an equivalent external process) |
| `measurements` | §5.4 — the software measurement program |
| `non-conformance-record` | §5.5 — non-conformance/defect management mechanism |

### Recording NASA-STD-8739.8B assurance and safety evidence

| Skill | What it does |
| --- | --- |
| `ivv-verification-record` | Records the 49 §4.4.2 IV&V provider verification duties. Only runs once `sa-ivv-coordination` has recorded IV&V as applicable — that's what generates the IV&V matrix it reads. |
| `sa-task-verification-management` | Records §4.3 Table 1 SA/safety task evidence for the NPR's Chapter 3 (Management) requirements — 45 of the catalog's 103 rows. |
| `sa-task-verification-management-engineering` | Same pattern for Chapter 4 (Engineering) requirements — 37 rows. |
| `sa-task-verification-supporting` | Same pattern for Chapter 5 (Supporting Life Cycle) requirements — the final 21 rows. All three skills read the same generated `sa-task-mapping-matrix.yaml`, each touching only its own chapter's rows. |

### Where the evidence lands

Everything is written into the project being assessed, under `docs/nasa-compliance/<subsystem>/`: `classification.yaml`, then `requirements-mapping-matrix.{md,yaml}`, and — where applicable — `ivv-mapping-matrix.{md,yaml}` and `sa-task-mapping-matrix.{md,yaml}`, plus each skill's own record file.

### Coverage and status

The bundled catalogs are working drafts derived from the standards in `reference/`, not certified reproductions of them.

- `data/swe-catalog.yaml` covers all 100 NPR 7150.2D Appendix C rows — see `data/CATALOG-COVERAGE.md`.
- `data/ivv-catalog.yaml` covers all 49 NASA-STD-8739.8B §4.4.2 rows.
- `data/sa-task-catalog.yaml` covers all 103 rows of §4.3 Table 1 — Chapter 3 (45), Chapter 4 (37), and Chapter 5 (21). See `data/SA-TASK-CATALOG-COVERAGE.md`.
- Appendix A hazard analysis is not yet covered.

Design rationale and build records for each piece of this layer live in `docs/superpowers/specs/` and `docs/superpowers/plans/`.

## Installing

This fork is not published to any plugin marketplace. Install it from this repository.

**Claude Code.** The repo carries its own marketplace manifest at `.claude-plugin/marketplace.json`, which names the marketplace `superpowers-dev` and the plugin `superpowers-nasa-swe`:

```bash
/plugin marketplace add adam-schneider-dev/superpowers-nasa-swe
/plugin install superpowers-nasa-swe@superpowers-dev
```

**Other harnesses.** Upstream Superpowers supports Antigravity, Codex App, Codex CLI, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, and Pi. Those instructions are preserved in [docs/installing.md](docs/installing.md) — note that they install upstream Superpowers, not this fork's compliance layer.

## How it works

It starts from the moment you fire up your coding agent. As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do.

1. **brainstorming** — activates before writing code. Refines rough ideas through questions, explores alternatives, and shows you the design in chunks short enough to actually read and digest. Saves a design document.
2. **using-git-worktrees** — activates after design approval. Creates an isolated workspace on a new branch, runs project setup, verifies a clean test baseline.
3. **writing-plans** — activates with an approved design. Breaks work into bite-sized tasks (2–5 minutes each), clear enough for an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing to follow. Every task has exact file paths, complete code, and verification steps. It emphasizes true red/green TDD, YAGNI (You Aren't Gonna Need It), and DRY.
4. **subagent-driven-development** or **executing-plans** — activates with a plan. Dispatches a fresh subagent per task with two-stage review (spec compliance, then code quality), or executes in batches with human checkpoints. It's not uncommon for your agent to work autonomously for a couple hours at a time without deviating from the plan you put together.
5. **test-driven-development** — activates during implementation. Enforces RED-GREEN-REFACTOR: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests.
6. **requesting-code-review** — activates between tasks. Reviews against the plan, reports issues by severity. Critical issues block progress.
7. **finishing-a-development-branch** — activates when tasks complete. Verifies tests, presents options (merge/PR/keep/discard), cleans up the worktree.

**The agent checks for relevant skills before any task.** Mandatory workflows, not suggestions. Because the skills trigger automatically, you don't need to do anything special. Your coding agent just has Superpowers.

The compliance skills layer onto this rather than replacing it: classify and generate the matrix once, then run the recording skills as each phase of work actually completes.

## Upstream skills library

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle (includes testing anti-patterns reference)

**Debugging**
- **systematic-debugging** - 4-phase root cause process (includes root-cause-tracing, defense-in-depth, condition-based-waiting techniques)
- **verification-before-completion** - Ensure it's actually fixed

**Collaboration**
- **brainstorming** - Socratic design refinement
- **writing-plans** - Detailed implementation plans
- **executing-plans** - Batch execution with checkpoints
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist
- **receiving-code-review** - Responding to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow
- **subagent-driven-development** - Fast iteration with two-stage review (spec compliance, then code quality)

**Meta**
- **writing-skills** - Create new skills following best practices (includes testing methodology)
- **using-superpowers** - Introduction to the skills system

## Philosophy

- **Test-Driven Development** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

Read [the original release announcement](https://blog.fsck.com/2025/10/09/superpowers/).

## Commercial Services

If you're using Superpowers in enterprise and could benefit from commercial support, additional tooling, or managed spending, please don't hesitate to drop us a line at sales@primeradiant.com.

## Contributing

The general contribution process for Superpowers is below. Keep in mind that we don't generally accept contributions of new skills and that any updates to skills must work across all of the coding agents we support.

1. Fork the repository
2. Switch to the 'dev' branch
3. Create a branch for your work
4. Follow the `writing-skills` skill for creating and testing new and modified skills
5. Submit a PR, being sure to fill in the pull request template.

Skill-behavior tests use the drill eval harness from [superpowers-evals](https://github.com/prime-radiant-inc/superpowers-evals/), cloned into `evals/` — see `evals/README.md` for setup. Plugin-infrastructure tests live at `tests/` and run via the relevant `run-*.sh` or `npm test`.

See `skills/writing-skills/SKILL.md` for the complete guide.

## License

MIT License - see LICENSE file for details

## Visual companion telemetry

Because skills and plugins don't provide any feedback to creators, we have no idea how many of you are using Superpowers. By default, the Prime Radiant logo on brainstorming's optional visual companion feature is loaded from our website. It includes the version of Superpowers in use. It does not include any details about your project, prompt, or coding agent. We don't see your clicks or anything about what you're building. This helps us have a rough idea of how many folks are using Superpowers and which version of Superpowers they're using. It's 100% optional. To disable this, set the environment variable `SUPERPOWERS_DISABLE_TELEMETRY` to any true value. Superpowers also honors Claude Code's `DISABLE_TELEMETRY` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` opt-outs.

## Community

Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the folks at [Prime Radiant](https://primeradiant.com).

- **Discord**: [Join us](https://discord.gg/35wsABTejz) for community support, questions, and sharing what you're building with Superpowers
- **Issues**: https://github.com/obra/superpowers/issues
- **Release announcements**: [Sign up](https://primeradiant.com/superpowers/) to get notified about new versions
