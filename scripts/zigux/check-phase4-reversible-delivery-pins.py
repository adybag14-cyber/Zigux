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
    "`PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=18338cd8134d9fd962edf9b177f82e5b9bd40108`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=a19e335ad46c6aba552d59fff4752b13d5f51c8b`",
    "`PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=0c38a3e7470f92b5b38da8659c548a51dbd09440`",
    "`PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=a6f9a63307ab24bf58fe574f5394fe87512d4d12`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=fc5728aa0ea4e46d1cebecd42fafc22b30746b38`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=946467383c7645434f6a0787486590fb443edd6b`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=ef333c03fa97927b2be0152b613fab727bb89a11`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=93aebf412639ccc1122a74b87201f57f6e7bfc99`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=76019df486d2582d3197a15cd00e7a050edcc766`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=ae44be2133b0bc9b7c13b3061c4eab0ecdff3ad0`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=c535d9f78360e0c3dfd4b93f8f01b1f4b4dd89b8`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=d6c5e647c33a8034d00a06fcb190d0fc484f55cb`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=795eafb366534f3d315565db05cace72a4009c4f`",
)

RECOVERED_NOTE_MARKERS = (
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "the broader review packet has partially recovered past the older all-missing state",
)

REMAINING_GAP_MARKERS = (
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "Authenticated contents reads in this runtime still flap on `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
)

ATOMIC64_DIRECT_MARKERS = (
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
)

NOTE_FOLLOW_UP_MARKER = (
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff"
)

WARNING_FOLLOW_UP_MARKER = NOTE_FOLLOW_UP_MARKER

NOTE_MIXED_PROVENANCE_MARKER = (
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff: current-head proof for the review checklist, the tests-root reminder, the repo-reality warning checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated local-only perf checker plus companion packet; archival anchor pins only for this note's self-reference and the reversible-delivery pin checker self-reference; public-raw current-tree proof that `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for those four companions until exact authenticated blob capture stabilizes."
)

WARNING_MIXED_PROVENANCE_MARKER = NOTE_MIXED_PROVENANCE_MARKER

NOTE_MARKERS = (
    STATUS_MARKERS
    + DIRECT_MARKERS
    + CURRENT_HEAD_BLOB_MARKERS
    + RECOVERED_NOTE_MARKERS
    + REMAINING_GAP_MARKERS
    + ATOMIC64_DIRECT_MARKERS
    + (
        NOTE_MIXED_PROVENANCE_MARKER,
        NOTE_FOLLOW_UP_MARKER,
    )
)

WARNING_MARKERS = (
    "DIRECT_READBACK_PACKET = (",
    "RECOVERED_NOTE_PACKET = (",
    "REMAINING_GAP_PACKET = (",
    "\"scripts/zigux/check-phase4-reversible-delivery-pins.py\",",
    "\"scripts/zigux/check-phase4-perf-baseline-packet.py\",",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff",
    WARNING_MIXED_PROVENANCE_MARKER,
    'REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"',
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16",
    "EXPECTED_PIN_SELF_TEST_CASES = 14",
    WARNING_FOLLOW_UP_MARKER + '.",',
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
    require_exact_self_test_count(
        note,
        NOTE.as_posix(),
        REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL,
        EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES,
    )
    require_exact_self_test_count(
        note,
        NOTE.as_posix(),
        PIN_SELF_TEST_COUNT_LABEL,
        EXPECTED_PIN_SELF_TEST_CASES,
    )


def baseline_note() -> str:
    lines = [
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "## Status",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=9c32cfdc6d3c8d449a10ede6b3380ef84ef8aad6`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=18338cd8134d9fd962edf9b177f82e5b9bd40108`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=a19e335ad46c6aba552d59fff4752b13d5f51c8b`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=0c38a3e7470f92b5b38da8659c548a51dbd09440`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=a6f9a63307ab24bf58fe574f5394fe87512d4d12`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=fc5728aa0ea4e46d1cebecd42fafc22b30746b38`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=946467383c7645434f6a0787486590fb443edd6b`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=ef333c03fa97927b2be0152b613fab727bb89a11`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=93aebf412639ccc1122a74b87201f57f6e7bfc99`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=76019df486d2582d3197a15cd00e7a050edcc766`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=ae44be2133b0bc9b7c13b3061c4eab0ecdff3ad0`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=c535d9f78360e0c3dfd4b93f8f01b1f4b4dd89b8`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=d6c5e647c33a8034d00a06fcb190d0fc484f55cb`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=795eafb366534f3d315565db05cace72a4009c4f`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14`",
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state even though the broader validator, build, and bitmap replay companions still remain unreadable in authenticated contents reads for this runtime.",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff. Authenticated contents reads in this runtime still flap on `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, but public raw fallback rereads now return those files on current `master`, matching the broader review packet's recovered note-and-checker companions.",
        "The recovered broader note pair therefore no longer overstates those validator-side and bitmap-side companions as absent current-head evidence. Treat this narrower handoff as the authoritative shared reminder while exact blob recapture for the validator, build, and bitmap replay companions still waits on steadier authenticated contents reads.",
        NOTE_MIXED_PROVENANCE_MARKER,
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
        NOTE_FOLLOW_UP_MARKER,
    ]
    return "\n".join(lines) + "\n"


def baseline_warning() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "DIRECT_READBACK_PACKET = (",
            '    "Documentation/zigux/phase4-reversible-delivery-evidence.md",',
            '    "Documentation/zigux/review-checklist.md",',
            '    "zigux/tests/README.md",',
            '    "scripts/zigux/check-phase4-repo-reality-warning.py",',
            '    "scripts/zigux/check-phase4-reversible-delivery-pins.py",',
            ")",
            "RECOVERED_NOTE_PACKET = (",
            '    "Documentation/zigux/phase4-gate-evidence.md",',
            '    "Documentation/zigux/phase4-validation-matrix.md",',
            '    "scripts/zigux/check-phase4-gate-evidence.py",',
            '    "scripts/zigux/check-phase4-remaining-gap-matrix.py",',
            ")",
            "REMAINING_GAP_PACKET = (",
            '    "scripts/zigux/validate-phase4.py",',
            '    "zigux/tests/phase4_build.zig",',
            '    "zigux/tests/bitmap_diff.zig",',
            '    "zigux/tests/phase4_bitmap_live_helper_replay.zig",',
            ")",
            'REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"',
            "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16",
            "EXPECTED_PIN_SELF_TEST_CASES = 14",
            '"scripts/zigux/check-phase4-reversible-delivery-pins.py",',
            '"scripts/zigux/check-phase4-perf-baseline-packet.py",',
            "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
            "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff",
            WARNING_MIXED_PROVENANCE_MARKER,
            WARNING_FOLLOW_UP_MARKER + '.",',
        ]
    ) + "\n"


def build_baseline_tree(root: Path) -> None:
    write(root, NOTE, baseline_note())
    write(root, REPO_REALITY_WARNING, baseline_warning())


def expect_failure(root: Path) -> int:
    try:
        check(root)
    except RuntimeError:
        return 1
    raise AssertionError("expected drift case to fail")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
        root = Path(tmp)

        build_baseline_tree(root)
        check(root)
        cases += 1

        mutations = (
            (NOTE, RECOVERED_NOTE_MARKERS[0], "Current direct contents reads in this run confirmed a different recovered note set."),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[0], "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[1], "`PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[2], "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=cccccccccccccccccccccccccccccccccccccccc`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[8], "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=dddddddddddddddddddddddddddddddddddddddd`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[9], "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[10], "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=ffffffffffffffffffffffffffffffffffffffff`"),
            (NOTE, CURRENT_HEAD_BLOB_MARKERS[14], "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=1212121212121212121212121212121212121212`"),
            (NOTE, REMAINING_GAP_MARKERS[-1], "The broader Phase 4 bitmap replay companions are still repo-reality gaps in this run"),
            (NOTE, "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`", "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=15`"),
            (NOTE, "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14`", "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=12`"),
            (NOTE, ATOMIC64_DIRECT_MARKERS[1], "Current direct contents reads for the atomic64 pair drifted"),
            (REPO_REALITY_WARNING, "EXPECTED_PIN_SELF_TEST_CASES = 14", "EXPECTED_PIN_SELF_TEST_CASES = 12"),
        )

        for rel, old, new in mutations:
            build_baseline_tree(root)
            write(root, rel, read(root, rel).replace(old, new, 1))
            cases += expect_failure(root)

    if cases != EXPECTED_PIN_SELF_TEST_CASES:
        print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=fail")
        print(f"expected {EXPECTED_PIN_SELF_TEST_CASES} self-test cases, saw {cases}")
        return 1

    print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass")
    print(f"{PIN_SELF_TEST_COUNT_LABEL}={cases}")
    print(f"{LEGACY_PIN_SELF_TEST_CASES_LABEL}={cases}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REVERSIBLE_DELIVERY_PINS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
