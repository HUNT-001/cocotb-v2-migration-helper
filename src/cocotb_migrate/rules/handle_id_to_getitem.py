from __future__ import annotations

import libcst as cst

from cocotb_migrate.diagnostics import Diagnostic


class HandleIdToGetitemRule(cst.CSTTransformer):
    RULE_NAME = "handle_id_to_getitem"

    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.changes = 0

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        func = updated_node.func

        if not (isinstance(func, cst.Attribute) and func.attr.value == "_id"):
            return updated_node

        if not updated_node.args:
            return updated_node

        first_arg = updated_node.args[0]
        if first_arg.keyword is not None or not isinstance(first_arg.value, cst.SimpleString):
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="warning",
                    message=(
                        "Found handle._id(...) with a non-literal first argument. "
                        "Manual migration required."
                    ),
                )
            )
            return updated_node

        # Only auto-fix zero extra args or exactly one keyword arg: extended=False
        rest = updated_node.args[1:]
        safe_rest = True
        for arg in rest:
            if arg.keyword is None:
                safe_rest = False
                break
            if arg.keyword.value != "extended":
                safe_rest = False
                break
            if not isinstance(arg.value, cst.Name) or arg.value.value != "False":
                safe_rest = False
                break

        if not safe_rest:
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="warning",
                    message=(
                        "Found handle._id(...) with unsupported extra arguments. "
                        "Manual migration required."
                    ),
                )
            )
            return updated_node

        self.changes += 1
        self.diagnostics.append(
            Diagnostic(
                rule=self.RULE_NAME,
                severity="info",
                message='Rewrote handle._id("name", extended=False) to handle["name"].',
            )
        )

        return cst.Subscript(
            value=func.value,
            slice=[
                cst.SubscriptElement(
                    slice=cst.Index(value=first_arg.value)
                )
            ],
        )