# Project working agreement

Read `PROJECT_STATUS.md`, `ASSIGNMENT.md`, `README.md`, `docs/DESIGN.md`, and
`docs/REFERENCES.md` before planning or changing this project. The references file
preserves the user's five original resources, professor clarification, and how
the reviewed material informed the design. The original assignment is authoritative;
technical reference defaults and examples are not additional course requirements.
CTFTiny is the benchmark goal; NYU documentation/package conventions support it.

## Code and complexity

- Prioritize clean, understandable code and reduce unnecessary complexity across
  the complete system, including setup, configuration, dependencies, and tests.
- Prefer straightforward functions, explicit data flow, clear responsibilities,
  and small dictionaries. Avoid custom application classes unless a concrete
  benefit has been discussed with the user. Function-based context managers are
  an accepted choice for resource cleanup.
- Remove duplication and use established capabilities when they reduce work we
  maintain. Avoid speculative features, general-purpose infrastructure, excessive
  helpers, and dependencies without a demonstrated benefit.
- Judge simplicity by how easily someone can understand, run, review, and maintain
  the project, not by line count. Preserve required controls and complete records.
- Keep tests and synthetic target support under `tests/`; keep the agent package
  focused on application behavior.

## Decisions and milestones

- Before consequential changes, explain what we currently do, the problem being
  solved, any relevant standard practice, reasonable alternatives, and the
  recommendation with its simplicity/maintenance tradeoffs. This includes
  programming style, major module boundaries, dependencies, model/API settings,
  container/process arrangements, benchmark reuse, and compatibility policies.
- Work in small approved milestones. Before starting, state the outcome and how
  it will be verified. Complete an approved milestone without repeatedly asking
  permission for routine details or necessary fixes.
- At each milestone's end, explain changes, actual verification, remaining limits,
  and the proposed next step. Update `PROJECT_STATUS.md` and relevant evidence,
  then stop for review before starting the next milestone.
- Preserve prior evidence as historical records. Run meaningful checks for changed
  behavior; do not add redundant tests or repeat broad suites without a reason.
- Real challenge attempts, pilots, scored selection/runs, improvement experiments,
  aggregation, and report/demo work require authorization for those later stages.

## Boundaries

- Execute model-controlled commands only in the isolated solver, never on the host
  or through an administrative target shell. Before isolation is verified, use
  test substitutes rather than enabling host execution.
- Keep expected answers, private metadata/source/build files, evaluator storage,
  credentials, host mounts, and the Docker socket outside the solver environment.
- Preserve enforced scope, resource limits, incident handling, submission records,
  and verification results. Do not expose expected answers separately in traces.
- Do not consult held-out evaluation flags, solutions, or write-ups during
  development/scoring. Generic reference-agent code and benchmark infrastructure
  can be reviewed; trusted verification loads answer keys programmatically.
