#!/usr/bin/env python3
"""Guard the current Phase 4 docs-root rollback reminder surface."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

DOCS_ROOT = Path("Documentation/zigux/README.md")
NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")

DOCS_DIRECT_PACKET = (
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)

DOCS_BROADER_GAPS = (
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "`zigux/tests/atomic64_diff.zig`",
    "`zigux/tests/runtime_atomic64_diff.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
)

DOCS_MARKERS = DOCS_DIRECT_PACKET + DOCS_BROADER_GAPS + (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "keep the broader Phase 4 repo-reality gaps explicit from the docs root too",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
)

NOTE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` on current `master`.",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, local-only perf companions, the bitmap-diff companions, or the roadmap-backed `atomic64_diff` pair are presently readable on current `master`.",
)

TESTS_MARKERS = (
    "current direct-readback Phase 4 rollback packet:",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
    "public current-`master` fallback rereads can still expose older broader Phase 4 companions",
)

SCRIPTS_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, and roadmap-backed `atomic64_diff` companions remain authenticated-readback repo-reality gaps on current `master`, so this note should stay aligned with that narrower direct-readback packet instead of treating public fallback visibility as the same thing as direct current-head proof",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    require(read(root, DOCS_ROOT), DOCS_MARKERS, DOCS_ROOT.as_posix())
    require(read(root, NOTE), NOTE_MARKERS, NOTE.as_posix())
    require(read(root, TESTS_README), TESTS_MARKERS, TESTS_README.as_posix())
    require(read(root, SCRIPTS_README), SCRIPTS_MARKERS, SCRIPTS_README.as_posix())


def baseline_docs_root() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            "Phase 4 notes",
            *DOCS_DIRECT_PACKET,
            "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
            "keep the broader Phase 4 repo-reality gaps explicit from the docs root too",
            *DOCS_BROADER_GAPS,
            "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
        ]
    ) + "\n"


def baseline_note() -> str:
    return "\n".join(
        [
            "# Phase 4 Reversible Delivery Evidence",
            *NOTE_MARKERS,
        ]
    ) + "\n"


def baseline_tests_readme() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            *TESTS_MARKERS,
        ]
    ) + "\n"


def baseline_scripts_readme() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            *SCRIPTS_MARKERS,
        ]
    ) + "\n"


def build_baseline_tree(root: Path) -> None:
    write(root, DOCS_ROOT, baseline_docs_root())
    write(root, NOTE, baseline_note())
    write(root, TESTS_README, baseline_tests_readme())
    write(root, SCRIPTS_README, baseline_scripts_readme())


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-docs-readme-surface-") as tmp:
            root = Path(tmp)
            build_baseline_tree(root)
            check(root)
            cases += 1

            docs_path = root / DOCS_ROOT
            docs_path.write_text(
                docs_path.read_text(encoding="utf-8").replace(
                    DOCS_BROADER_GAPS[10],
                    "`zigux/tests/bitmap_gap_drifted.zig`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected docs-root bitmap gap drift to fail")

            build_baseline_tree(root)
            docs_path = root / DOCS_ROOT
            docs_path.write_text(
                docs_path.read_text(encoding="utf-8").replace(
                    "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
                    "pending shared-CI perf wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected docs-root perf posture drift to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
                    "historical provenance wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected note provenance drift to fail")

            build_baseline_tree(root)
            tests_path = root / TESTS_README
            tests_path.write_text(
                tests_path.read_text(encoding="utf-8").replace(
                    TESTS_MARKERS[3],
                    "phase4 atomic64 warning drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests-root atomic64 drift to fail")

            build_baseline_tree(root)
            scripts_path = root / SCRIPTS_README
            scripts_path.write_text(
                scripts_path.read_text(encoding="utf-8").replace(
                    SCRIPTS_MARKERS[0],
                    "phase4 scripts summary drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected scripts-root summary drift to fail")

            build_baseline_tree(root)
            docs_path = root / DOCS_ROOT
            docs_path.write_text(
                docs_path.read_text(encoding="utf-8").replace(
                    DOCS_DIRECT_PACKET[4],
                    "`scripts/zigux/check-phase4-direct-pins-drifted.py`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected docs-root direct packet drift to fail")

        print("PHASE4_DOCS_README_SURFACE_SELF_TEST=pass")
        print(f"PHASE4_DOCS_README_SURFACE_SELF_TEST_CASE_COUNT={cases}")
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_DOCS_README_SURFACE=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_DOCS_README_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
