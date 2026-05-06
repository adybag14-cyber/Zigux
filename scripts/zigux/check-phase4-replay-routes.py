#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MATRIX_PATH = Path("Documentation/zigux/phase4-validation-matrix.md")
NOTE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_makefile",
    "makefile_helper_route_drift",
    "workflow_phase4_validate_step_drift",
    "matrix_atomic64_wrapper_drift",
    "gate_evidence_make_wrapper_drift",
]

REQUIRED_MAKE_LINES = [
    "PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-bitmap-diff phase4-bitmap-live-helper-replay phase4",
    "phase4-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "phase4-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4: phase4-validate phase4-test",
]

REQUIRED_WORKFLOW_LINES = [
    "- name: Validate Phase 4 diff gates",
    "        run: python3 scripts/zigux/validate-phase4.py",
    "      - name: Self-test Phase 4 validator",
    "        run: python3 scripts/zigux/validate-phase4.py --self-test",
    "      - name: Self-test Phase 4 gate evidence checker",
    "        run: python3 scripts/zigux/check-phase4-gate-evidence.py --self-test",
    "      - name: Run Phase 4 diff tests",
    "        run: zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_MATRIX_LINES = [
    "`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, matrix, and reviewer checklist aligned around the same bounded atomic64 handoff `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`",
    "`zigux/tests/bitmap_diff.zig` bounded broad bitmap rollback-readiness replay covering range, prefix, copy, exact `find_nth_bit`, and checksum-pinned threshold-replay checkpoints `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 entrypoint `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `make -C zigux phase4-bitmap-live-helper-replay` and `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
    "The matching Linux-style local wrappers are `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the lab matrix and the current `zigux/Makefile` replay surface stay aligned instead of leaving those local routes implicit beside the direct `python3` and `zig build` commands listed above.",
]

REQUIRED_NOTE_LINES = [
    "`zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`",
]


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def exact_line_count(text: str, expected_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == expected_line)


def require_exact_lines(text: str, prefix: str, expected_lines: list[str]) -> list[str]:
    missing: list[str] = []
    for expected_line in expected_lines:
        count = exact_line_count(text, expected_line)
        if count != 1:
            missing.append(f"{prefix}:exact_line_count:{expected_line}:{count}")
    return missing


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in [MAKEFILE_PATH, WORKFLOW_PATH, MATRIX_PATH, NOTE_PATH]:
        if not (root / relative_path).exists():
            missing.append(f"file:{relative_path}")
    if missing:
        return missing

    makefile_text = read_text(root, MAKEFILE_PATH)
    workflow_text = read_text(root, WORKFLOW_PATH)
    matrix_text = read_text(root, MATRIX_PATH)
    note_text = read_text(root, NOTE_PATH)

    missing.extend(require_exact_lines(makefile_text, "makefile", REQUIRED_MAKE_LINES))
    missing.extend(require_exact_lines(workflow_text, "workflow", REQUIRED_WORKFLOW_LINES))
    for expected_line in REQUIRED_MATRIX_LINES:
        if expected_line not in matrix_text:
            missing.append(f"matrix:missing_line:{expected_line}")
    for expected_line in REQUIRED_NOTE_LINES:
        if expected_line not in note_text:
            missing.append(f"note:missing_line:{expected_line}")
    return missing


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_fixture_tree(root: Path) -> None:
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(REQUIRED_MAKE_LINES) + "\n",
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(REQUIRED_WORKFLOW_LINES) + "\n",
    )
    write_text(
        root / MATRIX_PATH,
        "# Phase 4 Validation Matrix\n\n" + "\n".join(REQUIRED_MATRIX_LINES) + "\n",
    )
    write_text(
        root / NOTE_PATH,
        "# Phase 4 Gate Evidence\n\n" + "\n".join(f"- {line}" for line in REQUIRED_NOTE_LINES) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_replay_routes_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        missing = validate_root(root)
        assert missing == [], missing

        (root / MAKEFILE_PATH).unlink()
        missing = validate_root(root)
        assert missing == [f"file:{MAKEFILE_PATH}"], missing

        write_fixture_tree(root)
        write_text(
            root / MAKEFILE_PATH,
            read_text(root, MAKEFILE_PATH).replace(
                "phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
                "phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "makefile:exact_line_count:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig:2",
            "makefile:exact_line_count:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig:0",
        ], missing

        write_fixture_tree(root)
        write_text(
            root / WORKFLOW_PATH,
            read_text(root, WORKFLOW_PATH).replace(
                "run: python3 scripts/zigux/validate-phase4.py",
                "run: python3 scripts/zigux/check-phase4-gate-evidence.py",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "workflow:exact_line_count:        run: python3 scripts/zigux/validate-phase4.py:0"
        ], missing

        write_fixture_tree(root)
        write_text(
            root / MATRIX_PATH,
            read_text(root, MATRIX_PATH).replace(
                "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
                "`zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "matrix:missing_line:`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`"
        ], missing

        write_fixture_tree(root)
        write_text(
            root / NOTE_PATH,
            read_text(root, NOTE_PATH).replace(
                "`make -C zigux phase4-runtime-atomic64-diff-survey`",
                "`make -C zigux phase4-runtime-atomic64-diff`",
                1,
            ),
        )
        missing = validate_root(root)
        assert missing == [
            "note:missing_line:`zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone."
        ], missing

    print("PHASE4_REPLAY_ROUTE_CHECK_SELF_TEST=pass")
    print(f"PHASE4_REPLAY_ROUTE_CHECK_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE4_REPLAY_ROUTE_CHECK_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if the shipped Phase 4 Makefile, workflow, matrix, and gate-evidence route claims drift apart."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic route-alignment coverage in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_REPLAY_ROUTE_CHECK=fail")
        print("MISSING_PHASE4_REPLAY_ROUTE_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_REPLAY_ROUTE_MARKERS_END")
        return 1

    print("PHASE4_REPLAY_ROUTE_CHECK=pass")
    print(f"PHASE4_REPLAY_ROUTE_CHECK_CASE_COUNT={len(REQUIRED_MAKE_LINES) + len(REQUIRED_WORKFLOW_LINES) + len(REQUIRED_MATRIX_LINES) + len(REQUIRED_NOTE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
