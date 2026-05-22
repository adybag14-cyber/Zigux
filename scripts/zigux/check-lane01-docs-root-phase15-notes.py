#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

PHASE14_HEADING = "Phase 14 notes - "
PHASE15_HEADING = "Phase 15 notes - "

REQUIRED_MARKERS = (
    "Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md` - `Documentation/zigux/phase15-parity-scorecard-survey.md` - `Documentation/zigux/phase15-parity-scorecard.md` - `Documentation/zigux/phase15-indefinite-c-policy.md` - `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and `zigux/Makefile` keep the current parked governance packet reviewable without implying any Architecture Council approval for a freeze-map status change.",
    "- `make -C zigux phase15` reruns the same parked governance packet, and no Architecture Council approval is recorded yet for a freeze-map status change.",
    "- the shared Phase 15 docs-root handoff should also keep `scripts/zigux/check-phase15-scripts-readme-alignment.py` and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` visible as the current lane-owner vocabulary and packet-alignment surfaces, so the docs index stays caught up with the newer validation and policy-maintenance work already wired into the shipped build and make routes.",
)


def collect_errors(root: Path) -> list[str]:
    content = (root / DOCS_README_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            errors.append(f"missing:{marker}")

    phase14_index = content.find(PHASE14_HEADING)
    phase15_index = content.find(PHASE15_HEADING)

    if phase14_index == -1:
        errors.append(f"missing:{PHASE14_HEADING}")
    if phase15_index == -1:
        errors.append(f"missing:{PHASE15_HEADING}")

    if phase14_index != -1 and phase15_index != -1 and phase14_index >= phase15_index:
        errors.append("order:Phase 14 notes must appear before Phase 15 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return f"""# Zigux Documentation\n{PHASE14_HEADING}placeholder\n{REQUIRED_MARKERS[0]}\n{REQUIRED_MARKERS[1]}\n{REQUIRED_MARKERS[2]}\n"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase15_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_errors(root):
            raise AssertionError("baseline Phase 15 fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / DOCS_README_PATH, _sample_docs_readme().replace(marker + "\n", "", 1))
            errors = collect_errors(root)
            expected = [f"missing:{marker}"]
            if marker.startswith(PHASE15_HEADING):
                expected.append(f"missing:{PHASE15_HEADING}")
            if errors != expected:
                raise AssertionError(f"unexpected errors for marker removal: {errors}")
            case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            + REQUIRED_MARKERS[0]
            + "\n"
            f"{PHASE14_HEADING}placeholder\n"
            + REQUIRED_MARKERS[1]
            + "\n"
            + REQUIRED_MARKERS[2]
            + "\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 14 notes must appear before Phase 15 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 14/15 order case: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE15_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE15_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current docs-root Phase 15 reminder packet remains aligned."
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
        help="exercise the checker against synthetic Phase 15 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE15_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE15_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE15_NOTES_SECTION_ORDER=Phase14->Phase15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
