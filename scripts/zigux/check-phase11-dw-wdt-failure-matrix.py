#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md")
TEARDOWN_NOTE_PATH = Path("Documentation/zigux/phase11-dw-wdt-teardown-note.md")

REQUIRED_MATRIX_MARKERS = (
    "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "`phase11-dw-wdt-verify-tests`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "remove and teardown failure-mode split",
    "idle remove without a fabricated heartbeat",
    "idle remove with reset-backed quiesce",
    "idle IRQ-configured teardown without a fabricated stop path or continued heartbeat",
    "IRQ-mode teardown outcomes",
)

REQUIRED_TEARDOWN_MARKERS = (
    "continued-heartbeat semantics",
    "teardownSummary()",
    "removeSummary()",
    "drivers/watchdog/dw_wdt_verify.zig",
)


def collect_missing_markers(label: str, path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in (
        (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
        (TEARDOWN_NOTE_PATH, REQUIRED_TEARDOWN_MARKERS),
    ):
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        failures.extend(collect_missing_markers(rel_path.as_posix(), path, markers))
    return failures


def write_fixture_tree(root: Path) -> None:
    (root / VALIDATION_MATRIX_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / TEARDOWN_NOTE_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VALIDATION_MATRIX_PATH).write_text(
        "# Phase 11 DesignWare Watchdog Validation Matrix\n"
        "## Status\n"
        "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`\n"
        "- exact replay: `phase11-dw-wdt-verify-tests`\n"
        "- paired review surfaces: `drivers/watchdog/dw_wdt_verify.zig` and `Documentation/zigux/phase11-dw-wdt-teardown-note.md`\n"
        "- remove and teardown failure-mode split remains explicit\n"
        "- idle remove without a fabricated heartbeat stays reviewable\n"
        "- idle remove with reset-backed quiesce stays reviewable\n"
        "- idle IRQ-configured teardown without a fabricated stop path or continued heartbeat stays reviewable\n"
        "- IRQ-mode teardown outcomes stay reviewable\n",
        encoding="utf-8",
    )
    (root / TEARDOWN_NOTE_PATH).write_text(
        "# Phase 11 DesignWare Watchdog Teardown Note\n"
        "- stop() preserves continued-heartbeat semantics when hardware is non-stoppable\n"
        "- teardownSummary() keeps teardown outcomes explicit\n"
        "- removeSummary() keeps remove ownership explicit\n"
        "- paired replay lives in drivers/watchdog/dw_wdt_verify.zig\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, rel_path: Path, marker: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected not in failures:
        raise AssertionError(f"missing expected failure {expected!r}; got {failures!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11_dw_wdt_failure_matrix_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        for rel_path, markers in (
            (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
            (TEARDOWN_NOTE_PATH, REQUIRED_TEARDOWN_MARKERS),
        ):
            for marker in markers:
                expect_failure(root, rel_path, marker, f"{rel_path.as_posix()}:{marker}")
                write_fixture_tree(root)
                case_count += 1

        shutil.rmtree(root / VALIDATION_MATRIX_PATH.parent)
        failures = validate(root)
        expected_missing = f"missing_file:{VALIDATION_MATRIX_PATH.as_posix()}"
        if expected_missing not in failures:
            raise AssertionError(f"missing expected failure {expected_missing!r}; got {failures!r}")
        case_count += 1

    print(f"PHASE11_DW_WDT_FAILURE_MATRIX_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 11 dw_wdt failure-mode matrix packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("PHASE11_DW_WDT_FAILURE_MATRIX_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
