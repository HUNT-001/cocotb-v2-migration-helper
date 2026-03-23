# cocotb-v2-migration-helper

A prototype CST-based migration helper for upgrading legacy cocotb testbenches to cocotb 2.x.

## What this demo does

This prototype scans legacy cocotb Python code and performs a small set of targeted rewrites for common cocotb 2.x migration patterns.

### Implemented rules

- `cocotb.fork(...)` → `cocotb.start_soon(...)`
- `raise TestFailure("msg")` → `assert False, "msg"`
- `handle._id("sig", extended=False)` → `handle["sig"]`

## Why this matters

Migrating to cocotb 2.x is not always a simple text replacement problem. Some changes are safe to auto-fix, while others may require manual review because of semantic differences.

For example, `cocotb.start_soon()` does not behave exactly like `cocotb.fork()`. This prototype rewrites the call but also emits a warning so the user can review behavior-sensitive cases.

## Current prototype goals

- Show that cocotb migration can be treated as a syntax-aware transformation problem
- Separate safe rewrites from warn-only cases
- Preserve a path toward a more complete CLI migration assistant

## Project structure

```text
src/cocotb_migrate/
├─ cli.py
├─ diagnostics.py
├─ engine.py
└─ rules/
   ├─ fork_to_start_soon.py
   ├─ testfailure_to_assert.py
   └─ handle_id_to_getitem.py
Installation
pip install -e ".[dev]"
Run the demo
python -m cocotb_migrate.cli scan examples/legacy/legacy_input.py
Run tests
pytest
Example behavior

The tool:

rewrites safe migration patterns,
prints a unified diff,
emits diagnostics for review.
Next steps

Planned improvements include:

recursive directory scanning,
JSON diagnostics output,
more cocotb 2.x migration rules,
clearer classification into auto-fix vs warn-only vs manual-review cases.

---

### 4. Add a `DESIGN.md`
This is important because mentors like seeing engineering thinking, not just code.

Create `DESIGN.md` with this:

```md
# Design Notes: cocotb-v2-migration-helper

## Goal

Build a syntax-aware migration helper for cocotb 2.x upgrades.

The tool should assist users in migrating legacy cocotb test code by:
- automatically rewriting safe patterns,
- warning on behavior-sensitive patterns,
- leaving unsupported or ambiguous cases for manual review.

## Why CST instead of regex

Legacy cocotb migration involves Python syntax and API usage patterns that should be modified structurally, not via plain string replacement.

Concrete syntax tree tooling provides:
- more reliable matching,
- safer rewrites,
- better preservation of formatting and source structure.

## Current rule categories

### Auto-fix with warning
- `cocotb.fork(...)` → `cocotb.start_soon(...)`

Reason:
The replacement is syntactically straightforward, but behavior can differ because `start_soon()` schedules execution after the current task yields.

### Safe auto-fix
- `raise TestFailure("msg")` → `assert False, "msg"`
- `handle._id("sig", extended=False)` → `handle["sig"]`

Reason:
These patterns have direct migration equivalents in common simple cases.

### Manual review
Cases with:
- dynamic `_id(...)` arguments,
- unsupported `_id(...)` argument forms,
- complex `TestFailure(...)` usage,
- future coroutine/decorator migrations that may need broader context.

## CLI direction

The prototype currently supports:
- `scan path`

Planned commands:
- `fix path`
- recursive directory traversal
- JSON diagnostics output
- dry-run mode
- rule-level enable/disable controls

## Non-goals for the prototype

This prototype does not attempt to:
- fully migrate all cocotb 2.x changes,
- guarantee behavioral equivalence,
- perform simulator-aware validation.

## Future rule candidates

- `@cocotb.coroutine`
- deprecated logging access patterns
- runner API migration checks
- import cleanup for removed cocotb result APIs