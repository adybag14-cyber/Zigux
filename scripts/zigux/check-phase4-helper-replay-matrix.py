#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
MATRIX_PATH = ROOT / "Documentation/zigux/phase4-validation-matrix.md"

HELPER_REPLAY_ROW = (
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped "
    "`tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 "
    "entrypoint `Shared Subsystems Pod` `Shared Subsystems Pod` "
    "`python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file "
    "zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` "
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` "
    "`threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`"
)
HELPER_REPLAY_COMMAND = (
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`"
)
EXPECTED_SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_helper_replay_row",
    "missing_helper_replay_command",
    "duplicate_helper_replay_row",
    "duplicate_helper_replay_command",
]


def validate_matrix(text: str) -> list[str]:
    failures: list[str] = []

    row_count = text.count(HELPER_REPLAY_ROW)
    if row_count == 0:
        failures.append("phase4_helper_replay_matrix:missing_helper_replay_row")
    elif row_count != 1:
        failures.append(f"phase4_helper_replay_matrix:duplicate_helper_replay_row:{row_count}")

    command_count = text.count(HELPER_REPLAY_COMMAND)
    if command_count == 0:
        failures.append("phase4_helper_replay_matrix:missing_helper_replay_command")
    elif command_count != 1:
        failures.append(
            f"phase4_helper_replay_matrix:duplicate_helper_replay_command:{command_count}"
        )

    return failures


def run_check(root: Path) -> int:
    text = MATRIX_PATH.read_text(encoding="utf-8")
    failures = validate_matrix(text)
    if failures:
        print("PHASE4_HELPER_REPLAY_MATRIX_CHECK=fail")
        print("PHASE4_HELPER_REPLAY_MATRIX_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE4_HELPER_REPLAY_MATRIX_FAILURES_END")
        return 1

    print("PHASE4_HELPER_REPLAY_MATRIX_CHECK=pass")
    print("PHASE4_HELPER_REPLAY_MATRIX_ROW_COUNT=1")
    print("PHASE4_HELPER_REPLAY_MATRIX_COMMAND_COUNT=1")
    return 0


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    baseline = "\n".join(
        [
            "# Phase 4 Validation Matrix",
            "",
            HELPER_REPLAY_ROW,
            "",
        ]
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase4_helper_replay_matrix_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"

        _write(matrix_path, baseline)
        assert validate_matrix(matrix_path.read_text(encoding="utf-8")) == []

        _write(matrix_path, baseline.replace(HELPER_REPLAY_ROW, "", 1))
        assert validate_matrix(matrix_path.read_text(encoding="utf-8")) == [
            "phase4_helper_replay_matrix:missing_helper_replay_row",
            "phase4_helper_replay_matrix:missing_helper_replay_command",
        ]

        _write(matrix_path, baseline.replace(HELPER_REPLAY_COMMAND, "", 1))
        assert validate_matrix(matrix_path.read_text(encoding="utf-8")) == [
            "phase4_helper_replay_matrix:missing_helper_replay_row",
            "phase4_helper_replay_matrix:missing_helper_replay_command",
        ]

        _write(matrix_path, baseline + HELPER_REPLAY_ROW + "\n")
        assert validate_matrix(matrix_path.read_text(encoding="utf-8")) == [
            "phase4_helper_replay_matrix:duplicate_helper_replay_row:2",
            "phase4_helper_replay_matrix:duplicate_helper_replay_command:2",
        ]

        _write(matrix_path, baseline + HELPER_REPLAY_COMMAND + "\n")
        assert validate_matrix(matrix_path.read_text(encoding="utf-8")) == [
            "phase4_helper_replay_matrix:duplicate_helper_replay_command:2"
        ]

    print("PHASE4_HELPER_REPLAY_MATRIX_SELF_TEST=pass")
    print(f"PHASE4_HELPER_REPLAY_MATRIX_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print(
        "PHASE4_HELPER_REPLAY_MATRIX_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 4 helper-backed replay matrix row."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated checker coverage in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
