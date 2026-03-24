# cocotb-v2-migration-helper

A prototype CST-based migration helper for upgrading legacy cocotb testbenches to cocotb 2.x.

## Overview

`cocotb-v2-migration-helper` is a Python-based proof-of-concept tool that scans legacy cocotb test code and applies targeted migration rewrites for selected cocotb 2.x upgrade patterns.

This project is designed around a simple principle:

- auto-fix what is safe,
- warn on behavior-sensitive changes,
- leave ambiguous cases for manual review.

The current prototype demonstrates how cocotb migration can be treated as a syntax-aware source transformation problem instead of a fragile text-replacement script.

---

## Motivation

Upgrading legacy cocotb testbenches to cocotb 2.x is not always a simple search-and-replace exercise.

Some API updates can be rewritten mechanically, while others involve semantic differences that require developer review. A useful migration helper should therefore do more than blindly replace strings:

- it should parse code structurally,
- perform safe rewrites,
- emit clear diagnostics,
- and preserve a path toward human review where needed.

This prototype explores that direction using a CST-based approach.

---

## Current Features

### Auto-fix with warning
- `cocotb.fork(...)` → `cocotb.start_soon(...)`

This rewrite is applied automatically, but a warning is emitted because the scheduling behavior is not identical in all cases.

### Safe auto-fix
- `raise TestFailure("msg")` → `assert False, "msg"`
- `handle._id("sig", extended=False)` → `handle["sig"]`

These cases are rewritten automatically for simple supported patterns.

### Warn-only detection
- Detect `@cocotb.coroutine`

This pattern is currently flagged for manual migration and is not automatically rewritten.

---

## Why CST instead of regex?

This project uses a concrete syntax tree style approach because cocotb migration involves Python syntax and API structure, not just plain text replacement.

A CST-based design helps with:

- safer matching,
- more reliable rewrites,
- cleaner diagnostics,
- preservation of source layout,
- easier future expansion into additional rules.

---

## Example

### Input
```python
import cocotb
from cocotb.result import TestFailure
from cocotb.triggers import Timer


@cocotb.coroutine
def legacy_coroutine_helper(dut):
    yield Timer(1, units="ns")


async def helper(dut):
    dut._log.info("helper running")


@cocotb.test()
async def test_legacy(dut):
    task = cocotb.fork(helper(dut))
    signal_handle = dut._id("data_valid", extended=False)
    raise TestFailure("legacy failure path")
```
Output
```
import cocotb
from cocotb.result import TestFailure
from cocotb.triggers import Timer


@cocotb.coroutine
def legacy_coroutine_helper(dut):
    yield Timer(1, units="ns")


async def helper(dut):
    dut._log.info("helper running")


@cocotb.test()
async def test_legacy(dut):
    task = cocotb.start_soon(helper(dut))
    signal_handle = dut["data_valid"]
    assert False, "legacy failure path"

Diagnostics
coroutine_decorator_detector: Detected @cocotb.coroutine usage. Manual migration review recommended.
fork_to_start_soon: Rewrote cocotb.fork() to cocotb.start_soon(). Review behavior because scheduling semantics may differ.
testfailure_to_assert: Rewrote raise TestFailure("...") to assert False, "...".
handle_id_to_getitem: Rewrote handle._id("name", extended=False) to handle["name"].
```
Project Structure

cocotb-v2-migration-helper/
├─ pyproject.toml
├─ README.md
├─ DESIGN.md
├─ src/
│  └─ cocotb_migrate/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ diagnostics.py
│     ├─ engine.py
│     └─ rules/
│        ├─ __init__.py
│        ├─ coroutine_detector.py
│        ├─ fork_to_start_soon.py
│        ├─ testfailure_to_assert.py
│        └─ handle_id_to_getitem.py
├─ examples/
│  ├─ legacy/
│  │  └─ legacy_input.py
│  └─ expected/
│     └─ legacy_expected.py
└─ tests/
   └─ test_rules.py

Installation
1. Clone the repository
```git clone https://github.com/HUNT-001/cocotb-v2-migration-helper.git```
```cd cocotb-v2-migration-helper```
2. Create and activate a virtual environment
Windows PowerShell
```python -m venv .venv```
```.venv\Scripts\Activate.ps1```
Linux / macOS
```python -m venv .venv```
```source .venv/bin/activate```
3. Install dependencies
`pip install -e ".[dev]"
Usage
Scan a file
python -m cocotb_migrate.cli scan examples/legacy/legacy_input.py`

This will:

parse the file,
apply supported rewrites,
print a unified diff,
emit diagnostics.
Run tests
pytest
Current Rule Classification
Rule	Status	Behavior
cocotb.fork(...) → cocotb.start_soon(...)	Auto-fix with warning	Rewritten automatically, warning emitted
raise TestFailure("msg") → assert False, "msg"	Safe auto-fix	Rewritten automatically
handle._id("sig", extended=False) → handle["sig"]	Safe auto-fix	Rewritten automatically
@cocotb.coroutine	Warn-only	Detected and reported, not rewritten
Design Direction

The intended long-term workflow is:

Scan legacy cocotb code
Classify findings into:
safe auto-fix,
auto-fix with warning,
manual review
Rewrite supported patterns
Report diagnostics clearly to the user

This keeps the tool useful even before it reaches full migration coverage.

More details are documented in DESIGN.md
.

Current Limitations

This is an early prototype and intentionally limited in scope.

Current limitations include:

only a small subset of cocotb 2.x migration patterns are implemented,
no recursive directory traversal yet,
no JSON diagnostics output yet,
no auto-rewrite yet for deprecated coroutine-style code,
no simulator-backed validation of transformed testbenches.
Roadmap

Planned next steps:

recursive directory scanning,
fix command for writing changes back to disk,
JSON and machine-readable diagnostics,
additional cocotb 2.x migration rules,
clearer rule categories for:
safe auto-fix,
warn-only,
manual review,
improved reporting and rule-level controls.
Development

To make local changes:
```
pip install -e ".[dev]"
pytest
python -m cocotb_migrate.cli scan examples/legacy/legacy_input.py
```
Suggested development workflow:

add or refine a migration rule,
create/update fixture examples,
add a test,
verify CLI output and diagnostics.
Why this repo exists

This repository serves as a focused proof-of-concept for a cocotb 2.x migration assistant and demonstrates:

syntax-aware source rewriting,
migration rule classification,
warning-oriented developer guidance,
a practical base for a larger migration tool.
