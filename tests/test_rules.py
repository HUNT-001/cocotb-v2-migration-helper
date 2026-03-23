from pathlib import Path

from cocotb_migrate.engine import migrate_code


def test_demo_fixture_matches_expected() -> None:
    legacy = Path("examples/legacy/legacy_input.py").read_text(encoding="utf-8")
    expected = Path("examples/expected/legacy_expected.py").read_text(encoding="utf-8")

    result = migrate_code(legacy)

    assert result.migrated == expected
    assert result.changed is True
    assert len(result.diagnostics) == 4
    assert any(d.rule == "coroutine_decorator_detector" for d in result.diagnostics)