from dataclasses import dataclass


@dataclass
class Diagnostic:
    rule: str
    severity: str  # "info" | "warning"
    message: str