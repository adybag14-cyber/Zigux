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
    "`PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=cf5b7e8b7951fbab08751894a5582eb0a818f1f7`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=a19e335ad46c6aba552d59fff4752b13d5f51c8b`",
    "`PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=2159f357591633f21d60d4607cf4cbfa1d086f84`",
    "`PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=5143b3595c7f862a25efc32916249ed68c88a713`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=c744a2a91139b31b616affa80f0030586e906a80`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=2e7b03fa41b7fe705ce73158b55249c729caa2fd`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c8eef0dd5ab531e6a69acacd1f694772454af012`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=81b9a93e6cbb3e9f2c0a7d95ac4961d528756902`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=263f1d20190b807f38864f76810a57f1e79c5321`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=69bbaadbd6c88c5210ca91914e639bbc5f456829`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=5a37abd5f8c02414c9ca8e9d24043a8e8e29f428`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=049c1f90422a49ea83b5e50bf9f9fde9aa5bb501`",
    "`PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=ed1e702f3bd46386627b51cb60fde7b871b80215`",
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
    "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run",
)

ATOMIC64_DIRECT_MARKERS = (
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
)

FOLLOW_UP_MARKER = (
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md` now aligns with `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` on the recovered note pair, the recovered gate-evidence and remaining-gap checkers, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the scripts-root reminder still needs the same narrower repo-reality warning refresh and the validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff"
)

MIXED_PROVENANCE_MARKER = (
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff: current-head proof for the review checklist, the tests-root reminder, the repo-reality warning checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated local-only perf checker plus companion packet; archival anchor pins only for this note's self-reference and the reversible-delivery pin checker self-reference; and historical provenance only for the still-missing validator, build, and bitmap replay companions."
)

NOTE_MARKERS = (
    STATUS_MARKERS
    + DIRECT_MARKERS
    + CURRENT_HEAD_BLOB_MARKERS
    + RECOVERED_NOTE_MARKERS
    + REMAINING_GAP_MARKERS
    + ATOMIC64_DIRECT_MARKERS
    + (
        MIXED_PROVENANCE_MARKER,
        FOLLOW_UP_MARKER,
    )
)

WARNING_MARKERS = (
    "DIRECT_READBACK_PACKET = (",
    "RECOVERED_NOTE_PACKET = (",
    "REMAINING_GAP_PACKET = (",
    "\"scripts/zigux/check-phase4-reversible-delivery-pins.py\",",
    "\"scripts/zigux/check-phase4-perf-baseline-packet.py\",",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    MIXED_PROVENANCE_MARKER,
    'REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"',
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16",
    "EXPECTED_PIN_SELF_TEST_CASES = 14",
    FOLLOW_UP_MARKER + '.",',
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
        "  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=cf5b7e8b7951fbab08751894a5582eb0a818f1f7`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_BLOB_SHA=a19e335ad46c6aba552d59fff4752b13d5f51c8b`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=2159f357591633f21d60d4607cf4cbfa1d086f84`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=5143b3595c7f862a25efc32916249ed68c88a713`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=c744a2a91139b31b616affa80f0030586e906a80`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=2e7b03fa41b7fe705ce73158b55249c729caa2fd`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c8eef0dd5ab531e6a69acacd1f694772454af012`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=81b9a93e6cbb3e9f2c0a7d95ac4961d528756902`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=263f1d20190b807f38864f76810a57f1e79c5321`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=69bbaadbd6c88c5210ca91914e639bbc5f456829`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=5a37abd5f8c02414c9ca8e9d24043a8e8e29f428`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=049c1f90422a49ea83b5e50bf9f9fde9aa5bb501`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=ed1e702f3bd46386627b51cb60fde7b871b80215`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14`",
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state even though the broader validator, build, and bitmap replay companions still remain unreadable in authenticated contents reads for this runtime.",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=16` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=14` here",
        "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run: authenticated contents reads returned missing for `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`.",
        MIXED_PROVENANCE_MARKER,
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
        FOLLOW_UP_MARKER,
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
            "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run",
            MIXED_PROVENANCE_MARKER,
            FOLLOW_UP_MARKER + '.",',
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
