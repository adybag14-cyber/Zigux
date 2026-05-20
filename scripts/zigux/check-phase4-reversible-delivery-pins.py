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
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22
EXPECTED_PIN_SELF_TEST_CASES = 18

EXPECTED_ARCHIVAL_SHA_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=31f1d2ba21c371180593c9ad6de45b1fba0e04be`",
)

EXPECTED_CURRENT_HEAD_SHA_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=2529b35c9bfd2f750855db97cdc4ef2ba19b10b2`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=d8dd59e152e1d8c6be1278c976d3c54ab0786947`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=f2c6e213e20aa738914dd42abe76bd45e61cbc6a`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA=b19f58c82eeeacad6156c6fc3a398c52d8a546fa`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA=5acd6b1fd9db70bce8bd152194a58aab2c184eae`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=02fff445cf5c9be68eb169ffacd8f4c7c25fb5c9`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=065a43cd4984f898207e5a9a3ff9434ecaa2adca`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=984085b3db4de17e86646b0c1463ee6224bd8efc`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=a81a8b754d25c728d0f1b0334fca8752fa594379`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=18120c3d7244fb4c71450740c0f4aa336ba684b4`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=a28a7393df1b270de8c80c57c30287d548bd0c4e`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=fa4ab6b736a3eba358630a9913b447f77569ab29`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=11f2e26e0de96bbf8e327fca7409b732a090c5bb`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=aeb0cfb34be8e590703147c0e2fc77e1536fd759`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=7aa1ad4f41b5f7c7474ceac97c632bd8037e9714`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=75c533b819a0bb422e69c92a33a23da7c04d5af1`",
)

ATOMIC64_PACKET_SENTENCE = (
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair "
    "`zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet "
    "`zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`."
)

ATOMIC64_RETURNED_SENTENCE = (
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, "
    "`zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, "
    "so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader "
    "Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt."
)

NOTE_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    ATOMIC64_PACKET_SENTENCE,
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head proof for the docs-root reminder, the scripts-root reminder, the review checklist, the tests-root reminder, the repo-reality warning checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the atomic64 manifest-backed survey pair, and the dedicated local-only perf checker plus companion packet; archival anchor pins only for this note's self-reference and the reversible-delivery pin checker self-reference; public-raw current-tree proof that `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for those four companions until exact authenticated blob capture stabilizes.",
    ATOMIC64_RETURNED_SENTENCE,
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.",
)

WARNING_MARKERS = (
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22",
    "EXPECTED_PIN_SELF_TEST_CASES = 18",
    '\"scripts/zigux/check-phase4-reversible-delivery-pins.py\"',
    '\"scripts/zigux/check-phase4-perf-baseline-packet.py\"',
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.",
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

def require_exact_count(text: str, label: str, count_label: str, expected: int) -> None:
    matches = re.findall(rf"`{count_label}=(\d+)`", text)
    if not matches:
        raise RuntimeError(f"{label} is missing a numeric `{count_label}=...` marker")
    if any(int(value) != expected for value in matches):
        raise RuntimeError(f"{label} must carry `{count_label}={expected}` exactly")

def check(root: Path) -> None:
    note = read(root, NOTE)
    repo_warning = read(root, REPO_REALITY_WARNING)
    require(note, EXPECTED_ARCHIVAL_SHA_LINES + EXPECTED_CURRENT_HEAD_SHA_LINES + NOTE_MARKERS, NOTE.as_posix())
    require(repo_warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())
    require_exact_count(note, NOTE.as_posix(), REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL, EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES)
    require_exact_count(note, NOTE.as_posix(), PIN_SELF_TEST_COUNT_LABEL, EXPECTED_PIN_SELF_TEST_CASES)

def baseline_note() -> str:
    return "\n".join([
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "## Status",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
        *EXPECTED_ARCHIVAL_SHA_LINES,
        *EXPECTED_CURRENT_HEAD_SHA_LINES,
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        ATOMIC64_PACKET_SENTENCE,
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state even though the broader validator, build, and bitmap replay companions still remain unreadable in authenticated contents reads for this runtime.",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head proof for the docs-root reminder, the scripts-root reminder, the review checklist, the tests-root reminder, the repo-reality warning checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the atomic64 manifest-backed survey pair, and the dedicated local-only perf checker plus companion packet; archival anchor pins only for this note's self-reference and the reversible-delivery pin checker self-reference; public-raw current-tree proof that `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for those four companions until exact authenticated blob capture stabilizes.",
        ATOMIC64_RETURNED_SENTENCE,
        "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.",
    ]) + "\n"

def baseline_repo_warning() -> str:
    return "\n".join([
        "#!/usr/bin/env python3",
        'REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = \"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES\"',
        "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22",
        "EXPECTED_PIN_SELF_TEST_CASES = 18",
        '\\"scripts/zigux/check-phase4-reversible-delivery-pins.py\\"',
        '\\"scripts/zigux/check-phase4-perf-baseline-packet.py\\"',
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
        "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff.",
        "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.",
    ]) + "\n"

def build_baseline_tree(root: Path) -> None:
    write(root, NOTE, baseline_note())
    write(root, REPO_REALITY_WARNING, baseline_repo_warning())

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
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[0], "  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`"),
            (NOTE, EXPECTED_ARCHIVAL_SHA_LINES[1], "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[1], "  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=cccccccccccccccccccccccccccccccccccccccc`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[2], "  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=dddddddddddddddddddddddddddddddddddddddd`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[3], "  * `PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[4], "  * `PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA=ffffffffffffffffffffffffffffffffffffffff`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[11], "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=1111111111111111111111111111111111111111`"),
            (NOTE, EXPECTED_CURRENT_HEAD_SHA_LINES[12], "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=2222222222222222222222222222222222222222`"),
            (NOTE, "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`", "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=20`"),
            (NOTE, "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`", "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=15`"),
            (NOTE, "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head proof for the docs-root reminder, the scripts-root reminder, the review checklist, the tests-root reminder, the repo-reality warning checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the atomic64 manifest-backed survey pair, and the dedicated local-only perf checker plus companion packet; archival anchor pins only for this note's self-reference and the reversible-delivery pin checker self-reference; public-raw current-tree proof that `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for those four companions until exact authenticated blob capture stabilizes.", "The mixed provenance wording drifted."),
            (NOTE, "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state even though the broader validator, build, and bitmap replay companions still remain unreadable in authenticated contents reads for this runtime.", "Recovered-note wording drifted."),
            (NOTE, ATOMIC64_PACKET_SENTENCE, "Atomic64 packet wording drifted."),
            (NOTE, ATOMIC64_RETURNED_SENTENCE, "Atomic64 return wording drifted."),
            (NOTE, "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, and the now-returned validator, build, and bitmap replay companions, while exact blob-pin refresh for those broader companions remains the remaining authenticated-readback gap in this handoff.", "Follow-up wording drifted."),
            (REPO_REALITY_WARNING, "EXPECTED_PIN_SELF_TEST_CASES = 18", "EXPECTED_PIN_SELF_TEST_CASES = 12"),
            (REPO_REALITY_WARNING, '\\"scripts/zigux/check-phase4-reversible-delivery-pins.py\\"', '\\"scripts/zigux/check-phase4-other-file.py\\"'),
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