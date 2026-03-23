from __future__ import annotations

import libcst as cst

from cocotb_migrate.diagnostics import Diagnostic


class ForkToStartSoonRule(cst.CSTTransformer):
    RULE_NAME = "fork_to_start_soon"

    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.changes = 0

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        func = updated_node.func

        if (
            isinstance(func, cst.Attribute)
            and isinstance(func.value, cst.Name)
            and func.value.value == "cocotb"
            and func.attr.value == "fork"
        ):
            self.changes += 1
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="warning",
                    message=(
                        "Rewrote cocotb.fork() to cocotb.start_soon(). "
                        "Review behavior: start_soon() schedules execution after the current task yields."
                    ),
                )
            )
            return updated_node.with_changes(
                func=func.with_changes(attr=cst.Name("start_soon"))
            )

        return updated_node