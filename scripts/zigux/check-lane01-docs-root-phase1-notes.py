#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

PHASE1_HEADING = "Phase 1 notes - "
PHASE2_HEADING = "Phase 2 notes - "

REQUIRED_MARKERS = (
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)


def collect_errors(root: Path) -> list[str]:
    content = (root / DOCS_README_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            errors.append(f"missing:{marker}")

    phase1_index = content.find(PHASE1_HEADING)
    phase2_index = content.find(PHASE2_HEADING)

    if phase1_index == -1:
        errors.append(f"missing:{PHASE1_HEADING}")
    if phase2_index == -1:
        errors.append(f"missing:{PHASE2_HEADING}")

    if phase1_index != -1 and phase2_index != -1 and phase1_index >= phase2_index:
        errors.append("order:Phase 1 notes must appear before Phase 2 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return f"""# Zigux Documentation
{REQUIRED_MARKERS[0]}
{REQUIRED_MARKERS[1]}
{REQUIRED_MARKERS[2]}
{REQUIRED_MARKERS[3]}
{REQUIRED_MARKERS[4]}
{PHASE2_HEADING}placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase1_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_errors(root):
            raise AssertionError("baseline Phase 1 fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / DOCS_README_PATH, _sample_docs_readme().replace(marker + "\n", "", 1))
            errors = collect_errors(root)
            expected = [f"missing:{marker}"]
            if marker.startswith(PHASE1_HEADING):
                expected.append(f"missing:{PHASE1_HEADING}")
            if errors != expected:
                raise AssertionError(f"unexpected errors for marker removal: {errors}")
            case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            f"{PHASE2_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS)
            + "\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 1 notes must appear before Phase 2 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 1/2 order case: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE1_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE1_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current docs-root Phase 1 reminder packet remains aligned."
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
        help="exercise the checker against synthetic Phase 1 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE1_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE1_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE1_NOTES_SECTION_ORDER=Phase1->Phase2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())