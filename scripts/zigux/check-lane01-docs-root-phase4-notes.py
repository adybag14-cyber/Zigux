#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

PHASE3_HEADING = "Phase 3 notes - "
PHASE4_HEADING = "Phase 4 notes - "
PHASE6_HEADING = "Phase 6 notes - "

REQUIRED_MARKERS = (
    "Phase 4 notes - `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/atomic64_diff.zig` roadmap wrapper, its shared `zigux/tests/runtime_atomic64_diff.zig` backing replay, the manifest-backed `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` handoff survey, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` wired through the shared `zigux/tests/phase4_build.zig` entrypoint and the bootstrap workflow.",
    "- `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` now keep the exact-readback packet, rollback owners, lab or CI replay matrix, the approved local-only benchmark-command and acceptable-limit split, and the still-pending shared-CI perf-promotion posture explicit for the shipped Phase 4 gates instead of leaving that narrower validator-backed packet implied from the scripts root and tests root alone.",
)


def collect_errors(root: Path) -> list[str]:
    content = (root / DOCS_README_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            errors.append(f"missing:{marker}")

    phase3_index = content.find(PHASE3_HEADING)
    phase4_index = content.find(PHASE4_HEADING)
    phase6_index = content.find(PHASE6_HEADING)

    if phase3_index == -1:
        errors.append(f"missing:{PHASE3_HEADING}")
    if phase4_index == -1:
        errors.append(f"missing:{PHASE4_HEADING}")
    if phase6_index == -1:
        errors.append(f"missing:{PHASE6_HEADING}")

    if phase3_index != -1 and phase4_index != -1 and phase3_index >= phase4_index:
        errors.append("order:Phase 3 notes must appear before Phase 4 notes")
    if phase4_index != -1 and phase6_index != -1 and phase4_index >= phase6_index:
        errors.append("order:Phase 4 notes must appear before Phase 6 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return f"""# Zigux Documentation
{PHASE3_HEADING}placeholder
{REQUIRED_MARKERS[0]}
{REQUIRED_MARKERS[1]}
{PHASE6_HEADING}placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase4_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_errors(root):
            raise AssertionError("baseline Phase 4 fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / DOCS_README_PATH, _sample_docs_readme().replace(marker + "\n", "", 1))
            errors = collect_errors(root)
            expected = [f"missing:{marker}"]
            if marker.startswith(PHASE4_HEADING):
                expected.append(f"missing:{PHASE4_HEADING}")
            if errors != expected:
                raise AssertionError(f"unexpected errors for marker removal: {errors}")
            case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            f"{PHASE4_HEADING}placeholder\n"
            f"{PHASE3_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS)
            + "\n"
            f"{PHASE6_HEADING}placeholder\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 3 notes must appear before Phase 4 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 3/4 order case: {errors}")
        case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            f"{PHASE3_HEADING}placeholder\n"
            f"{PHASE6_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS)
            + "\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 4 notes must appear before Phase 6 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 4/6 order case: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE4_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE4_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current docs-root Phase 4 reminder packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Phase 4 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE4_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE4_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE4_NOTES_SECTION_ORDER=Phase3->Phase4->Phase6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
