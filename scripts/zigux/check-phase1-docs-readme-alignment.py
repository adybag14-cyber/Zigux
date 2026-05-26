#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 1 notes",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards:",
    "keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)


def collect_missing_markers(root: Path) -> list[str]:
    source = (root / DOCS_README_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            missing.append(f"docs_readme:{marker}")
    return missing


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_docs_readme() -> str:
    return """# Zigux Documentation
Phase 1 notes
`Documentation/zigux/phase1-host-helper-lane-sequencing.md`
`Documentation/zigux/phase1-closure.md`
`Documentation/zigux/review-checklist.md`
`zigux/tests/README.md`
`zigux/tests/fixtures/phase1_helper_manifest.json`
`scripts/zigux/README.md`
`scripts/zigux/validate-phase1-closure.py`
`scripts/zigux/check-phase1-string-review-packet.py`
`scripts/zigux/check-phase1-direct-owner-markers.py`
`scripts/zigux/check-phase1-shared-reminder-packet.py`
`scripts/zigux/check-phase1-bench.py`
keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.
the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards:
keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.
`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
"""


def write_sample_root(root: Path) -> None:
    write_text(root / DOCS_README_PATH, sample_docs_readme())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_docs_readme_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_missing_markers(root):
            raise AssertionError("baseline docs README fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS[1:]:
            write_sample_root(root)
            write_text(
                root / DOCS_README_PATH,
                sample_docs_readme().replace(marker + "\n", "", 1),
            )
            missing = collect_missing_markers(root)
            expected = [f"docs_readme:{marker}"]
            if missing != expected:
                raise AssertionError(
                    f"unexpected missing markers for {marker!r}: {missing}"
                )
            case_count += 1

    print("PHASE1_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 1 summary still names the current closure packet honestly."
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
        help="exercise the checker against synthetic docs-root fixtures",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("PHASE1_DOCS_README_ALIGNMENT=pass")
    print(f"PHASE1_DOCS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
