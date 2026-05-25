#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md` - `Documentation/zigux/phase14-core-boundary-traceability.md` - `Documentation/zigux/phase14-release-boundary-survey.md` - `Documentation/zigux/phase14-productization-gap-survey.md` - `Documentation/zigux/phase14-shared-smoke-current-master-gap.md` - `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md` - `Documentation/zigux/phase14-rcu-tree-survey.md` - `Documentation/zigux/phase14-skbuff-bridge-survey.md` - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `zigux/tests/phase14_end_to_end_smoke_manifest.json` keep the bounded Phase 14 docs-root packet explicit through the recovered shared-smoke documentation layer, the directly readable route, tests-root, rollback-threshold, validator, dedicated RCU rollback, and release-boundary guards, the machine-readable shared-smoke manifest, and the returned `phase14-validate` split without promoting the missing `phase14-smoke`, `phase14-test`, or `phase14` wrappers into current proof.",
    "* the current docs-root Phase 14 reminder packet should stay parked on `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase14_end_to_end_smoke_manifest.json` so the docs root matches the same recovered study-only packet already carried by the shared smoke note, the release-boundary note, the dedicated RCU survey companion, the returned skbuff, freeze-map, and study-only accounting companions, the scripts-root reminder, the tests-root reminder, and the manifest-backed machine-readable split.",
    "* `zigux/Makefile`, `scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the current returned `phase14-validate` route, the aligned tests-root reminder, the rollback-threshold contract, the dedicated RCU rollback guard, the shared validator surface, and the release-facing exact-count posture explicit from the docs root while the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent on current `master`.",
    "* keep the returned anchor-local study surfaces explicit too: `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and `zigux/tests/phase14_ring_buffer_survey.zig` are current directly readable evidence again, `Documentation/zigux/phase14-rcu-tree-survey.md` is current directly readable freeze-in-C evidence again, while `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` stay exact-readback gaps in this lane.",
    "* keep the docs-root Phase 14 note bounded below live workqueue execution, ring-buffer publication ownership, skbuff lifetime ownership, RCU grace-period ownership, or any Phase 15 freeze-map status change; the honest same-lane task here is shared reminder truthfulness around the returned study-only packet and the single `make -C zigux phase14-validate` gate.",
)

FORBIDDEN_MARKERS = ("Phase 15 notes -",)
SECTION_ORDER = ("Phase 12 notes", "Phase 14 notes")


def collect_missing_markers(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    return [f"readme:{marker}" for marker in REQUIRED_MARKERS if marker not in readme]


def collect_forbidden_markers(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    return [f"unexpected:{marker}" for marker in FORBIDDEN_MARKERS if marker in readme]


def check_section_order(root: Path) -> str | None:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    positions: list[int] = []
    for marker in SECTION_ORDER:
        position = readme.find(marker)
        if position == -1:
            return f"missing_section:{marker}"
        positions.append(position)
    if positions != sorted(positions):
        return "section_order:Phase12->Phase14"
    return None


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation

Phase 12 notes

placeholder

Phase 14 notes - `Documentation/zigux/phase14-end-to-end-smoke-survey.md` - `Documentation/zigux/phase14-core-boundary-traceability.md` - `Documentation/zigux/phase14-release-boundary-survey.md` - `Documentation/zigux/phase14-productization-gap-survey.md` - `Documentation/zigux/phase14-shared-smoke-current-master-gap.md` - `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md` - `Documentation/zigux/phase14-rcu-tree-survey.md` - `Documentation/zigux/phase14-skbuff-bridge-survey.md` - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `zigux/tests/phase14_end_to_end_smoke_manifest.json` keep the bounded Phase 14 docs-root packet explicit through the recovered shared-smoke documentation layer, the directly readable route, tests-root, rollback-threshold, validator, dedicated RCU rollback, and release-boundary guards, the machine-readable shared-smoke manifest, and the returned `phase14-validate` split without promoting the missing `phase14-smoke`, `phase14-test`, or `phase14` wrappers into current proof.
* the current docs-root Phase 14 reminder packet should stay parked on `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase14_end_to_end_smoke_manifest.json` so the docs root matches the same recovered study-only packet already carried by the shared smoke note, the release-boundary note, the dedicated RCU survey companion, the returned skbuff, freeze-map, and study-only accounting companions, the scripts-root reminder, the tests-root reminder, and the manifest-backed machine-readable split.
* `zigux/Makefile`, `scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the current returned `phase14-validate` route, the aligned tests-root reminder, the rollback-threshold contract, the dedicated RCU rollback guard, the shared validator surface, and the release-facing exact-count posture explicit from the docs root while the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent on current `master`.
* keep the returned anchor-local study surfaces explicit too: `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and `zigux/tests/phase14_ring_buffer_survey.zig` are current directly readable evidence again, `Documentation/zigux/phase14-rcu-tree-survey.md` is current directly readable freeze-in-C evidence again, while `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` stay exact-readback gaps in this lane.
* keep the docs-root Phase 14 note bounded below live workqueue execution, ring-buffer publication ownership, skbuff lifetime ownership, RCU grace-period ownership, or any Phase 15 freeze-map status change; the honest same-lane task here is shared reminder truthfulness around the returned study-only packet and the single `make -C zigux phase14-validate` gate.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase14_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 Phase 14 fixture should pass")
        if collect_forbidden_markers(root):
            raise AssertionError("baseline fixture should not trigger forbidden markers")
        order_error = check_section_order(root)
        if order_error is not None:
            raise AssertionError(f"baseline section order should pass, got {order_error}")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / README_PATH, _sample_readme().replace(marker, "", 1))
            missing = collect_missing_markers(root)
            expected = [f"readme:{marker}"]
            if missing != expected:
                raise AssertionError(f"unexpected missing markers: {missing}")
            _write(root / README_PATH, _sample_readme())
            case_count += 1

        _write(root / README_PATH, _sample_readme() + "\nPhase 15 notes - stale follow-up\n")
        forbidden = collect_forbidden_markers(root)
        if forbidden != ["unexpected:Phase 15 notes -"]:
            raise AssertionError(f"unexpected forbidden markers: {forbidden}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Phase 12 notes\n\nplaceholder\n\nPhase 14 notes",
                "Phase 14 notes\n\nplaceholder\n\nPhase 12 notes",
                1,
            ),
        )
        order_error = check_section_order(root)
        if order_error != "section_order:Phase12->Phase14":
            raise AssertionError(f"unexpected order error: {order_error}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE14_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE14_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 14 reminder packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 Phase 14 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    forbidden = collect_forbidden_markers(args.root)
    order_error = check_section_order(args.root)
    if missing or forbidden or order_error is not None:
        for item in missing:
            print(f"ERROR: {item}")
        for item in forbidden:
            print(f"ERROR: {item}")
        if order_error is not None:
            print(f"ERROR: {order_error}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE14_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE14_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE14_NOTES_SECTION_ORDER=Phase12->Phase14")
    print("LANE01_DOCS_ROOT_PHASE14_NOTES_PHASE15_PACKET=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
