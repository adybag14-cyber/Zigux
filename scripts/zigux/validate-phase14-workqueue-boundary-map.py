#!/usr/bin/env python3
"""Fail-close the current Phase 14 workqueue boundary map."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase14-workqueue-boundary-map.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")

REQUIRED_NOTE_MARKERS = (
    "`PHASE14_STATUS=workqueue_boundary_map_landed`",
    "`PHASE14_LANE_KEY=P14-L02`",
    "`PHASE14_SCOPE=kernel/workqueue bridge boundary mapping`",
    "`PHASE14_POSTURE=study_only_wrapper_first`",
    "`kernel/workqueue.c` is a core-adjacent boundary-study target first, not a rewrite target",
    "### Keep in C",
    "### Candidate wrapper-first seam",
    "### Future bridge contract constraints",
    "- worker-pool creation, destruction, and global lifecycle",
    "- flush, cancel, drain, and barrier execution semantics",
    "- queue request classification at the API boundary",
    "- explicit queue target selection metadata",
    "- non-owning shape checks for `work_struct`, `delayed_work`, and queue flags",
    "- any bridge must stay metadata-only on first entry",
    "- the bridge may validate shape, flags, and queue-selection intent, but it must not own worker execution",
    "- the bridge must treat `schedule_work*`, `queue_work*`, `mod_delayed_work*`, `flush_*`, and cancel paths as distinct call families with different rollback expectations",
    "- no Phase 14 follow-up may present queue completion, wakeup policy, timer ownership, or forward-progress guarantees as Zig-owned behavior",
    "The smallest honest future bridge seam is a contract layer that describes queue-submission intent without moving scheduling or worker execution out of C.",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "- `kernel/workqueue.c`",
    "- future-only reference: `kernel/workqueue_bridge.zig`",
    "- a shipped `kernel/workqueue_bridge.zig`",
    "- permission to move workqueue execution, timers, flush/cancel semantics, or worker-pool ownership into Zig",
    "- parity evidence for `kernel/workqueue.c`",
    "- an Architecture Council decision to move this anchor beyond study-only posture",
    "- a metadata-only wrapper contract for queue-submission intent",
    "- a call-family audit that separates submission, delayed-work, and flush/cancel surfaces",
    "- a validator that keeps this boundary map aligned with the freeze-map and study-only accounting notes",
)

REQUIRED_FREEZE_MAP_MARKERS = (
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

REQUIRED_STUDY_ONLY_MARKERS = (
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.",
    "### `kernel/workqueue.c`",
    "- posture: `study_only`",
    "- a direct Zigux bridge for `kernel/workqueue.c`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    required = {
        NOTE_PATH: REQUIRED_NOTE_MARKERS,
        FREEZE_MAP_PATH: REQUIRED_FREEZE_MAP_MARKERS,
        STUDY_ONLY_PATH: REQUIRED_STUDY_ONLY_MARKERS,
    }

    for relative_path, markers in required.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    _write(root / NOTE_PATH, _read(Path(__file__).resolve().parents[2] / NOTE_PATH))
    _write(root / FREEZE_MAP_PATH, _read(Path(__file__).resolve().parents[2] / FREEZE_MAP_PATH))
    _write(root / STUDY_ONLY_PATH, _read(Path(__file__).resolve().parents[2] / STUDY_ONLY_PATH))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase14_workqueue_boundary_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE14_WORKQUEUE_BOUNDARY_MAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (NOTE_PATH, REQUIRED_NOTE_MARKERS[0]),
            (NOTE_PATH, REQUIRED_NOTE_MARKERS[10]),
            (FREEZE_MAP_PATH, REQUIRED_FREEZE_MAP_MARKERS[1]),
            (STUDY_ONLY_PATH, REQUIRED_STUDY_ONLY_MARKERS[1]),
        )
        for relative_path, marker in cases:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE14_WORKQUEUE_BOUNDARY_MAP_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE14_WORKQUEUE_BOUNDARY_MAP_SELF_TEST=pass")
    print("PHASE14_WORKQUEUE_BOUNDARY_MAP_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 14 workqueue boundary map."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 14 workqueue boundary map",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE14_WORKQUEUE_BOUNDARY_MAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print("PHASE14_WORKQUEUE_BOUNDARY_MAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
