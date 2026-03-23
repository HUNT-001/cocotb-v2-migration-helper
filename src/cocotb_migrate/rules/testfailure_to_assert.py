from __future__ import annotations

import libcst as cst

from cocotb_migrate.diagnostics import Diagnostic


class TestFailureToAssertRule(cst.CSTTransformer):
    RULE_NAME = "testfailure_to_assert"

    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.changes = 0

    def _is_testfailure_call(self, expr: cst.BaseExpression | None) -> bool:
        if not isinstance(expr, cst.Call):
            return False

        func = expr.func
        if isinstance(func, cst.Name) and func.value == "TestFailure":
            return True

        if isinstance(func, cst.Attribute) and func.attr.value == "TestFailure":
            return True

        return False

    def leave_Raise(
        self, original_node: cst.Raise, updated_node: cst.Raise
    ) -> cst.BaseSmallStatement:
        exc = updated_node.exc

        if exc is None or not self._is_testfailure_call(exc):
            return updated_node

        assert isinstance(exc, cst.Call)

        # Safe auto-fix only for 0 or 1 positional argument.
        positional_args = [a for a in exc.args if a.keyword is None]
        keyword_args = [a for a in exc.args if a.keyword is not None]

        if keyword_args or len(positional_args) > 1:
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="warning",
                    message=(
                        "Found complex TestFailure(...) usage that was not auto-fixed. "
                        "Manual migration to assert is required."
                    ),
                )
            )
            return updated_node

        self.changes += 1
        if len(positional_args) == 0:
            self.diagnostics.append(
                Diagnostic(
                    rule=self.RULE_NAME,
                    severity="info",
                    message="Rewrote raise TestFailure() to assert False.",
                )
            )
            return cst.Assert(test=cst.Name("False"))

        self.diagnostics.append(
            Diagnostic(
                rule=self.RULE_NAME,
                severity="info",
                message='Rewrote raise TestFailure("...") to assert False, "...".',
            )
        )
        return cst.Assert(
            test=cst.Name("False"),
            msg=positional_args[0].value,
        )