# Security Policy

Noetheris is defensive research infrastructure. Reports should focus on issues that affect correctness, integrity, reproducibility, misleading security interpretation, or unsafe behavior in repository code.

## Supported Versions

The active development branch is supported. Release branches should state their supported status in release notes.

## Responsible Disclosure

Send security reports to the project maintainers through a private channel before public disclosure. Include:

- affected component and version or commit;
- reproduction steps;
- expected and observed behavior;
- security impact;
- whether the issue can cause incorrect certificate acceptance, unsafe cryptographic interpretation, or uncontrolled execution.

## Scope

In scope:

- certificate validation flaws;
- nondeterministic or incorrect optimization outputs;
- unsafe parsing behavior;
- dependency or supply-chain risks;
- documentation that could imply unsupported cryptographic capabilities.

Out of scope:

- claims that toy lattice examples do not assess production PQC security;
- absence of cloud quantum credentials;
- performance limitations of exhaustive local solvers.

Noetheris does not provide offensive cryptographic tooling. Any contribution that turns toy examples into attacks against real deployments is outside the project scope.
