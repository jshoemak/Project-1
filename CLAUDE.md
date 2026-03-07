# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working in this repository.

## Project Overview

**Repository**: Project-1
**Owner**: jshoemak
**Status**: Early-stage / skeleton repository

This project currently contains only an initial scaffold. As the codebase grows, this file should be updated to reflect the actual structure, conventions, and workflows.

---

## Repository Structure

```
Project-1/
├── CLAUDE.md       # This file — AI assistant guidance
└── README.md       # Project readme
```

No application source code, dependency manifests, or build configuration exists yet. All structure below is aspirational guidance for when the project is built out.

---

## Git Workflow

### Branches

- **`master`** — stable, production-ready code
- **`claude/<description>-<id>`** — branches used by AI assistants for automated work

### Commit Conventions

Use clear, imperative commit messages:

```
Add user authentication module
Fix null pointer in payment service
Refactor database connection pooling
```

- Keep the subject line under 72 characters
- Use the body to explain *why*, not *what*

### Push Procedure

Always push with upstream tracking:

```bash
git push -u origin <branch-name>
```

Branch names for AI-driven work must start with `claude/` and include a session-specific suffix (e.g., `claude/add-feature-XxYyZz`). Pushing to any other branch requires explicit user permission.

---

## Development Guidelines (for when code is added)

### General Conventions

- Prefer editing existing files over creating new ones
- Avoid over-engineering — implement only what is needed for the current task
- Do not add comments, docstrings, or type annotations to code that was not changed
- Validate at system boundaries (user input, external APIs); trust internal code
- Never introduce command injection, XSS, SQL injection, or other OWASP Top 10 vulnerabilities

### Adding Dependencies

When introducing a package manager, document the choice here and include:
- The dependency file (e.g., `package.json`, `requirements.txt`, `go.mod`)
- A `scripts` or `Makefile` section covering install, build, test, and lint

### Environment Variables

- Never commit secrets or credentials
- Document required environment variables in a `.env.example` file
- Load secrets from environment, not from code

### Testing

- Write tests for new functionality before marking work complete
- All tests must pass before committing
- Document the test command here once a framework is chosen

### Linting / Formatting

- Enforce consistent style via a linter/formatter (ESLint, Black, gofmt, etc.)
- Configure the tool at the repo root and document the command here

---

## AI Assistant Checklist

When working in this repository, AI assistants should:

1. **Read before editing** — always read a file before modifying it
2. **Stay on the designated branch** — never push to `master` without explicit approval
3. **Commit incrementally** — make small, focused commits with clear messages
4. **Update this file** — if the codebase structure, conventions, or tooling changes, update CLAUDE.md accordingly
5. **Ask before destructive actions** — deleting files, force-pushing, or dropping data requires user confirmation
6. **Match existing style** — follow the patterns already present in the code rather than introducing new idioms

---

## Updating This File

This document should be kept current. Update it whenever:

- A new language, framework, or major library is added
- The directory structure changes significantly
- New development workflows or CI/CD pipelines are introduced
- Coding conventions are established or changed

_Last updated: 2026-03-07_
