#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

PHASE4_MATRIX = "Documentation/zigux/phase4-validation-matrix.md"
HELPER_HEADING = "### `zigux/tests/phase4_bitmap_live_helper_replay.zig`"
MATRIX_HEADING = "## Lab And CI Matrix"

HELPER_SECTION_REQUIRED_MARKERS = [
    HELPER_HEADING,
    "- owner: `Shared Subsystems Pod`",
    "- rollback owner: `Shared Subsystems Pod`",
    "- fallback path: keep `zigux/tests/bitmap_diff.zig`, the current C anchor at `lib/test_bitmap.c`, and the shipped helper sources as the truthful rollback surface if the helper-backed replay regresses and has to leave the shared Phase 4 entrypoint",
    "- perf threshold status: correctness-only gate today; it inherits `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
]
HELPER_SECTION_EXACT_ONCE_MARKERS = HELPER_SECTION_REQUIRED_MARKERS[1:]
MATRIX_EXACT_ONCE_MARKERS = [
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 entrypoint",
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`",
    "`threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
]


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return ""

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if heading == HELPER_HEADING and lines[index].startswith(("### ", "## ")):
            end = index
            break
        if heading == MATRIX_HEADING and lines[index].startswith("## ") and lines[index] != MATRIX_HEADING:
            end = index
            break
    return "\n".join(lines[start:end]) + "\n"


def validate_text(text: str) -> list[str]:
    missing: list[str] = []
    helper_section = _extract_section(text, HELPER_HEADING)
    matrix_section = _extract_section(text, MATRIX_HEADING)

    if not helper_section:
        return [f"phase4_bitmap_helper_ownership:{HELPER_HEADING}"]
    if not matrix_section:
        return [f"phase4_bitmap_helper_route:{MATRIX_HEADING}"]

    for marker in HELPER_SECTION_REQUIRED_MARKERS:
        if marker not in helper_section:
            missing.append(f"phase4_bitmap_helper_ownership:{marker}")
    for marker in HELPER_SECTION_EXACT_ONCE_MARKERS:
        count = helper_section.count(marker)
        if count != 1:
            missing.append(f"phase4_bitmap_helper_ownership:exact_once:{marker}:{count}")
    for marker in MATRIX_EXACT_ONCE_MARKERS:
        count = matrix_section.count(marker)
        if count != 1:
            missing.append(f"phase4_bitmap_helper_route:exact_once:{marker}:{count}")
    return missing


def validate_root(root: Path) -> list[str]:
    return validate_text((root / PHASE4_MATRIX).read_text(encoding="utf-8"))


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _replace_in_section(text: str, heading: str, old: str, new: str, count: int = 1) -> str:
    section = _extract_section(text, heading)
    return text.replace(section, section.replace(old, new, count), 1)


def _fixture_matrix() -> str:
    return "\n".join(
        [
            "# Phase 4 Validation Matrix",
            "",
            "### `zigux/tests/bitmap_diff.zig`",
            "- owner: `Shared Subsystems Pod`",
            "- rollback owner: `Shared Subsystems Pod`",
            "",
            HELPER_HEADING,
            "- owner: `Shared Subsystems Pod`",
            "- rollback owner: `Shared Subsystems Pod`",
            "- fallback path: keep `zigux/tests/bitmap_diff.zig`, the current C anchor at `lib/test_bitmap.c`, and the shipped helper sources as the truthful rollback surface if the helper-backed replay regresses and has to leave the shared Phase 4 entrypoint",
            "- perf threshold status: correctness-only gate today; it inherits `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
            "",
            MATRIX_HEADING,
            "`zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 entrypoint",
            "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`",
            "`threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`",
            "",
        ]
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_bitmap_helper_ownership_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(root, PHASE4_MATRIX, _fixture_matrix())

        assert validate_root(root) == []

        owner_missing = _replace_in_section(
            _fixture_matrix(),
            HELPER_HEADING,
            "- owner: `Shared Subsystems Pod`\n",
            "",
            1,
        )
        _write(root, PHASE4_MATRIX, owner_missing)
        assert validate_root(root) == [
            "phase4_bitmap_helper_ownership:- owner: `Shared Subsystems Pod`",
            "phase4_bitmap_helper_ownership:exact_once:- owner: `Shared Subsystems Pod`:0",
        ]

        rollback_missing = _replace_in_section(
            _fixture_matrix(),
            HELPER_HEADING,
            "- rollback owner: `Shared Subsystems Pod`\n",
            "",
            1,
        )
        _write(root, PHASE4_MATRIX, rollback_missing)
        assert validate_root(root) == [
            "phase4_bitmap_helper_ownership:- rollback owner: `Shared Subsystems Pod`",
            "phase4_bitmap_helper_ownership:exact_once:- rollback owner: `Shared Subsystems Pod`:0",
        ]

        route_missing = _replace_in_section(
            _fixture_matrix(),
            MATRIX_HEADING,
            "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`\n",
            "",
            1,
        )
        _write(root, PHASE4_MATRIX, route_missing)
        assert validate_root(root) == [
            "phase4_bitmap_helper_route:exact_once:`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`:0"
        ]

    print("PHASE4_BITMAP_HELPER_OWNERSHIP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 4 helper-backed bitmap ownership block or lab replay row drifts."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated checker coverage in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_BITMAP_HELPER_OWNERSHIP_PACKET=fail")
        print("PHASE4_BITMAP_HELPER_OWNERSHIP_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE4_BITMAP_HELPER_OWNERSHIP_FAILURES_END")
        return 1

    print("PHASE4_BITMAP_HELPER_OWNERSHIP_PACKET=pass")
    print(f"PHASE4_BITMAP_HELPER_OWNERSHIP_SOURCE={PHASE4_MATRIX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
