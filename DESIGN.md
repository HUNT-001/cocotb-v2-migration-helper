# Design Notes: cocotb-v2-migration-helper

## Goal

Build a syntax-aware migration helper for cocotb 2.x upgrades.

The tool should help users migrate legacy cocotb Python test code by:
- automatically rewriting safe patterns,
- warning on behavior-sensitive patterns,
- leaving ambiguous or unsupported cases for manual review.

## Why CST instead of regex

cocotb migration involves Python syntax and API usage patterns that should be transformed structurally rather than by plain string replacement.

A CST-based approach helps with:
- reliable matching,
- safer rewrites,
- preservation of source structure and formatting.

## Rule categories

### Auto-fix with warning
- cocotb.fork(...) -> cocotb.start_soon(...)

Reason:
This rewrite is syntactically direct, but semantics may differ because start_soon() schedules execution after the current task yields.

### Safe auto-fix
- aise TestFailure("msg") -> ssert False, "msg"
- handle._id("sig", extended=False) -> handle["sig"]

Reason:
These have direct migration equivalents in common simple cases.

### Warn-only / manual review
- @cocotb.coroutine

Reason:
Coroutine-style code may require broader migration context and should be flagged before any automatic rewrite is attempted.

## Current prototype scope

The prototype currently demonstrates:
- CST-based rule application,
- unified diff output,
- diagnostics for behavior-sensitive or manual-review cases.

## CLI direction

Current command:
- scan path

Planned commands:
- ix path
- recursive directory traversal
- JSON diagnostics output
- dry-run mode
- rule-level enable/disable controls

## Non-goals

This prototype does not yet aim to:
- fully migrate all cocotb 2.x changes,
- guarantee behavioral equivalence,
- validate transformed code against simulators.

## Future rule candidates

- deprecated coroutine migration assistance
- logging migration checks
- runner API migration checks
- import cleanup for removed cocotb result APIs
