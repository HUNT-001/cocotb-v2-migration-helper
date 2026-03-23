from __future__ import annotations

import libcst as cst

from cocotb_migrate.diagnostics import Diagnostic


class CoroutineDecoratorDetectorRule(cst.CSTTransformer):
    RULE_NAME = "coroutine_decorator_detector"

    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.changes = 0

    def visit_Decorator(self, node: cst.Decorator) -> None:
        decorator = node.decorator

        if (
            isinstance(decorator, cst.Attribute)
            and isinstance(decorator.value, cst.Name)
            and decorator.value.value == "cocotb"
            and decorator.attr.value == "coroutine"
        ):
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="warning",
                    message=(
                        "Detected @cocotb.coroutine usage. "
                        "This pattern is deprecated and should be reviewed for manual migration."
                    ),
                )
            )