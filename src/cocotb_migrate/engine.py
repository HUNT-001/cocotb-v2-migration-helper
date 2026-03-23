from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import difflib

import libcst as cst

from cocotb_migrate.diagnostics import Diagnostic
from cocotb_migrate.rules import (
    CoroutineDecoratorDetectorRule,
    ForkToStartSoonRule,
    HandleIdToGetitemRule,
    TestFailureToAssertRule,
)


RULES = [
    CoroutineDecoratorDetectorRule,
    ForkToStartSoonRule,
    TestFailureToAssertRule,
    HandleIdToGetitemRule,
]


@dataclass
class MigrationResult:
    original: str
    migrated: str
    diagnostics: list[Diagnostic]

    @property
    def changed(self) -> bool:
        return self.original != self.migrated

    def unified_diff(self, path: str = "input.py") -> str:
        diff = difflib.unified_diff(
            self.original.splitlines(keepends=True),
            self.migrated.splitlines(keepends=True),
            fromfile=f"{path}:before",
            tofile=f"{path}:after",
        )
        return "".join(diff)


def migrate_code(source: str) -> MigrationResult:
    module = cst.parse_module(source)
    diagnostics: list[Diagnostic] = []

    for rule_cls in RULES:
        rule = rule_cls()
        module = module.visit(rule)
        diagnostics.extend(rule.diagnostics)

    return MigrationResult(
        original=source,
        migrated=module.code,
        diagnostics=diagnostics,
    )


def migrate_file(path: Path, write: bool = False) -> MigrationResult:
    source = path.read_text(encoding="utf-8")
    result = migrate_code(source)
    if write and result.changed:
        path.write_text(result.migrated, encoding="utf-8")
    return result