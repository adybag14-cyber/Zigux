#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery repo-reality handoff."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
LEGACY_PIN_SELF_TEST_CASES_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES"
REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16
EXPECTED_PIN_SELF_TEST_CASES = 14

STATUS_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here",
)

DIRECT_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)

CURRENT_HEAD_BLOB_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=9c32cfdc6d3c8d449a10ede6b3380ef84ef8aad6`",
    "`PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=75c9e6f18ceb0bab8e3758ebb8117d1292413914`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=a19e335ad46c6aba552d59fff4752b13d5f51c8b`",
    "`PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=e94b6038894382e8934c8251a74d1778bb053725`",
    "`PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=76e8269d4e7bd172debabe42122fd7cebdee2131`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=c744a2a91139b31b616affa80f0030586e906a80`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c8eef0dd5ab531e6a69acacd1f694772454af012`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=096311d4b448b7c6f6f5b0fe4da220794c6cf94a`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=b0152bdc215a6139ee06cc6c661c2a2d489af07c`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=5fdd363b7319e925d0a18d7be848100b0b44a6e9`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=5a37abd5f8c02414c9ca8e9d24043a8e8e29f428`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=049c1f90422a49ea83b5e50bf9f9fde9aa5bb501`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=ed1e702f3bd46386627b51cb60fde7b871b80215`",
)

RECOVERED_NOTE_MARKERS = (
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "the broader review packet has partially recovered past the older all-missing state",
)

REMAINING_GAP_MARKERS = (
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
)

ATOMIC64_DIRECT_MARKERS = (
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
)

NOTE_MARKERS = (
    STATUS_MARKERS
    + DIRECT_MARKERS
    + CURRENT_HEAD_BLOB_MARKERS
    + RECOVERED_NOTE_MARKERS
    + REMAINING_GAP_MARKERS
    + ATOMIC64_DIRECT_MARKERS
    + (
        "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
        "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff: current-head proof for this note's self-reference, the review checklist, the tests-root reminder, the repo-reality warning checker, the reversible-delivery pin checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated local-only perf checker plus companion packet, and historical provenance only for the still-missing gate-evidence checker, remaining-gap checker, validator, build, and bitmap replay companions",
        "The remaining shared reminder follow-up from the older mixed-readback packet is now closed: `zigux/tests/README.md` now aligns with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` on the recovered note pair, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the broader checker, validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff",
    )
)

WARNING_MARKERS = (
    "DIRECT_READBACK_PACKET = (",
    "RECOVERED_NOTE_PACKET = (",
    "REMAINING_GAP_PACKET = (",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` on current `master`",
    "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff",
    "REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = \"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES\"",
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16",
    "EXPECTED_PIN_SELF_TEST_CASES = 14",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now closed: `zigux/tests/README.md` now aligns with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` on the recovered note pair, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the broader checker, validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff.",
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


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_exact_self_test_count(text: str, label: str, count_label: str, expected: int) -> None:
    matches = re.findall(rf"`{count_label}=(\d+)`", text)
    if not matches:
        raise RuntimeError(f"{label} is missing a numeric `{count_label}=...` marker")
    if any(int(value) != expected for value in matches):
        raise RuntimeError(f"{label} must carry `{count_label}={expected}` exactly")


def check(root: Path) -> None:
    note = read(root, NOTE)
    repo_warning = read(root, REPO_REALITY_WARNING)
    require(note, NOTE_MARKERS, NOTE.as_posix())
    require(repo_warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())
    require_exact_self_test_count(note, NOTE.as_posix(), REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL, EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES)
    require_exact_self_test_count(note, NOTE.as_posix(), PIN_SELF_TEST_COUNT_LABEL, EXPECTED_PIN_SELF_TEST_CASES)


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
            root = Path(tmp)
            for rel in (NOTE, REPO_REALITY_WARNING):
                src = args.root.resolve() / rel
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            check(root)
            cases += 1

            note_path = root / NOTE
            warning_path = root / REPO_REALITY_WARNING

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    RECOVERED_NOTE_MARKERS[0],
                    "Current direct contents reads in this run confirmed a different recovered note set.",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected recovered-note marker drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[0],
                    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected note blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[1],
                    "`PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected repo-warning checker blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[2],
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=cccccccccccccccccccccccccccccccccccccccc`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected pin checker blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[7],
                    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=dddddddddddddddddddddddddddddddddddddddd`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected workflow-route checker blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[8],
                    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected makefile blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[9],
                    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=ffffffffffffffffffffffffffffffffffffffff`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected workflow blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    CURRENT_HEAD_BLOB_MARKERS[13],
                    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=1212121212121212121212121212121212121212`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected sequencing-note blob pin drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
                    "The broader Phase 4 bitmap replay companions are still repo-reality gaps in this run",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected remaining-gap summary drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`",
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=15`",
                    1,
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected repo-warning self-test count drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            warning_path.write_text(
                warning_path.read_text(encoding="utf-8").replace(
                    "EXPECTED_PIN_SELF_TEST_CASES = 14",
                    "EXPECTED_PIN_SELF_TEST_CASES = 12",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected pin-self-test expectation drift to fail")
            warning_path.write_text((args.root.resolve() / REPO_REALITY_WARNING).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14`",
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12`",
                    1,
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected pin self-test count drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
                    "Current direct contents reads for the atomic64 pair drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected atomic64 direct-readback drift to fail")
            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")

        print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass")
        print(f"{PIN_SELF_TEST_COUNT_LABEL}={cases}")
        print(f"{LEGACY_PIN_SELF_TEST_CASES_LABEL}={cases}")
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REVERSIBLE_DELIVERY_PINS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
