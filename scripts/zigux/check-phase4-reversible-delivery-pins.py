#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery repo-reality handoff."""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
TESTS_README_PACKET = Path("scripts/zigux/check-phase4-tests-readme-packet.py")
DOCS_README = Path("Documentation/zigux/README.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
LEGACY_PIN_SELF_TEST_CASES_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32
EXPECTED_PIN_SELF_TEST_CASES = 20
VALIDATOR_MEMBER_LINE = "Current direct-readback shared validator member: `scripts/zigux/validate-phase4.py`."
PERF_BASELINE_CHECKER_LINE = (
    "Current direct-readback dedicated local-only perf checkers: "
    "`scripts/zigux/check-phase4-perf-baseline-packet.py` and "
    "`scripts/zigux/check-phase4-perf-threshold-matrix.py`."
)

STATIC_SHA_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=5d125f0e20b3378b2d5ff1b94d0779557a980cee`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=ebfa4ef208f3cca0439c96eb6c0e26c752a5c4c1`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=a125ef1084c82485782634dcb1b3e855482b7cc9`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=0ca3d60957fcda306a3d9cf915ecf405ffc82080`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=0b1032c1de0aa4f4250422887bdd53e93797438f`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=f88ef141412c62ee03077a5656630eaa9f2b5185`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=c289ee59d6373c28d090ab738aa966c110b4ea79`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=ea1d90419ea8984b71ac347ad20863f7bf07e7a7`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=87b72410a69b90e0cd4377ac30f7c47d0d9943c2`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=7580d3292a60c7fe8c88879c1a064834023cf5f2`",
)
CURRENT_HEAD_BLOB_PINS = (
    ("PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA", REPO_REALITY_WARNING),
    ("PHASE4_REVERSIBLE_DELIVERY_TESTS_README_PACKET_CHECKER_BLOB_SHA", TESTS_README_PACKET),
    ("PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA", CHECKLIST),
    ("PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA", TESTS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA", DOCS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA", SCRIPTS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA", VALIDATOR),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA", PERF_BASELINE_CHECKER),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA", PERF_MANIFEST),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA", PERF_SURVEY),
)
EXPECTED_STATUS_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`",
)
EXPECTED_PACKET_MEMBER_LINES = (
    "Current direct-readback packet members:",
    "  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "  * `Documentation/zigux/README.md`",
    "  * `Documentation/zigux/review-checklist.md`",
    "  * `zigux/tests/README.md`",
    "  * `scripts/zigux/README.md`",
    "  * `scripts/zigux/check-phase4-repo-reality-warning.py`",
    "  * `scripts/zigux/check-phase4-tests-readme-packet.py`",
    "  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)
EXPECTED_RECOVERY_MARKERS = (
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
    "Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here. Keep `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` explicit as the shared lab-matrix control surface for that same ownership split so the recovered broader packet stays aligned without collapsing the narrower direct-readback handoff into parked-gap or perf-local wording.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
)
NOTE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    VALIDATOR_MEMBER_LINE,
    PERF_BASELINE_CHECKER_LINE,
    "Current direct-readback dedicated local-only perf companion members:",
    "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
    "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
    "current-head blob-pin proof for `scripts/zigux/validate-phase4.py` on `master`",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
)

WARNING_MARKERS = (
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
    "EXPECTED_PIN_SELF_TEST_CASES = 20",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def gitBlobSha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def current_head_blob_pin_line(root: Path, label: str, rel: Path) -> str:
    return f"  * `{label}={gitBlobSha(root / rel)}`"


def find_status_line(text: str, label: str) -> str:
    prefix = f"  * `{label}="
    for line in text.splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line
    raise RuntimeError(f"missing status line for {label}")


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_exact_count(text: str, marker: str, expected_count: int, label: str) -> None:
    actual_count = text.count(marker)
    if actual_count != expected_count:
        raise RuntimeError(
            f"{label} expected {expected_count} instances of {marker!r}, found {actual_count}"
        )


def require_current_head_blob_pins(root: Path, note: str) -> None:
    missing = [
        current_head_blob_pin_line(root, label, rel)
        for label, rel in CURRENT_HEAD_BLOB_PINS
        if current_head_blob_pin_line(root, label, rel) not in note
    ]
    if missing:
        raise RuntimeError(f"{NOTE.as_posix()} is missing current-head blob pins: {missing}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    warning = read(root, REPO_REALITY_WARNING)
    require(
        note,
        STATIC_SHA_LINES + EXPECTED_STATUS_LINES + NOTE_MARKERS + EXPECTED_PACKET_MEMBER_LINES + EXPECTED_RECOVERY_MARKERS,
        NOTE.as_posix(),
    )
    require_exact_count(note, PERF_BASELINE_CHECKER_LINE, 1, NOTE.as_posix())
    require_current_head_blob_pins(root, note)
    require(warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())


def _baseline_other(path: Path) -> str:
    if path == REPO_REALITY_WARNING:
        return _baseline_warning()
    return f"placeholder for {path.as_posix()}\n"


def _baseline_note(root: Path) -> str:
    lines = [
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "## Status",
        *STATIC_SHA_LINES,
        *(current_head_blob_pin_line(root, label, rel) for label, rel in CURRENT_HEAD_BLOB_PINS),
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`",
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "",
        "Current direct-readback packet members:",
        "  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
        "  * `Documentation/zigux/README.md`",
        "  * `Documentation/zigux/review-checklist.md`",
        "  * `zigux/tests/README.md`",
        "  * `scripts/zigux/README.md`",
        "  * `scripts/zigux/check-phase4-repo-reality-warning.py`",
        "  * `scripts/zigux/check-phase4-tests-readme-packet.py`",
        "  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
        "",
        VALIDATOR_MEMBER_LINE,
        "",
        PERF_BASELINE_CHECKER_LINE,
        "",
        "Current direct-readback dedicated local-only perf companion members:",
        "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
        "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
        "",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
        "Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here. Keep `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` explicit as the shared lab-matrix control surface for that same ownership split so the recovered broader packet stays aligned without collapsing the narrower direct-readback handoff into parked-gap or perf-local wording.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head proof for the docs-root reminder, the scripts-root reminder, the review checklist, the tests-root reminder, the repo-reality warning checker, the tests-readme packet checker, the reversible-delivery pin checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the atomic64 manifest-backed survey pair, and the dedicated local-only perf checker plus companion packet; archival anchor pin only for this note's self-reference; current-head blob-pin proof for `scripts/zigux/validate-phase4.py` on `master`; public-raw current-tree proof that `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for that broader build-and-bitmap trio until exact authenticated blob capture stabilizes.",
        "",
    ]
    return "\n".join(lines) + "\n"


def _baseline_warning() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
            "EXPECTED_PIN_SELF_TEST_CASES = 20",
            "scripts/zigux/check-phase4-reversible-delivery-pins.py",
            "scripts/zigux/check-phase4-perf-baseline-packet.py",
            "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
        ]
    ) + "\n"


def _build_baseline_tree(root: Path) -> None:
    required_files = {
        NOTE,
        REPO_REALITY_WARNING,
        TESTS_README_PACKET,
        DOCS_README,
        CHECKLIST,
        TESTS_README,
        SCRIPTS_README,
        VALIDATOR,
        PERF_BASELINE_CHECKER,
        PERF_MANIFEST,
        PERF_SURVEY,
    }
    for rel in required_files:
        if rel == NOTE:
            continue
        write(root, rel, _baseline_other(rel))
    write(root, NOTE, _baseline_note(root))


def _expect_failure(root: Path, rel: Path, old: str | None, new: str | None) -> int:
    _build_baseline_tree(root)
    if old is None:
        (root / rel).unlink()
    else:
        write(root, rel, read(root, rel).replace(old, new, 1))
    try:
        check(root)
    except RuntimeError:
        return 1
    raise AssertionError(f"expected failure for {rel}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
        root = Path(tmp)
        _build_baseline_tree(root)
        check(root)
        for label, _ in CURRENT_HEAD_BLOB_PINS:
            _build_baseline_tree(root)
            line = find_status_line(read(root, NOTE), label)
            cases += _expect_failure(root, NOTE, line, line.replace(line[-41:-1], "0" * 40))
        cases += _expect_failure(
            root,
            NOTE,
            STATIC_SHA_LINES[0],
            "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=" + ("0" * 40) + "`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`",
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=29`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`",
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=19`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `scripts/zigux/check-phase4-tests-readme-packet.py`",
            "  * `scripts/zigux/check-phase4-tests-review-packet.py`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            PERF_BASELINE_CHECKER_LINE,
            "Current direct-readback dedicated local-only perf checker: `scripts/zigux/old-phase4-perf-baseline-packet.py`.",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.",
            "Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names the landed rollback owners, but the exact owner map is omitted here.",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
            "The broader Phase 4 validator, build, and bitmap replay companions still count as current-`master` gaps in this handoff.",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here. Keep `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` explicit as the shared lab-matrix control surface for that same ownership split so the recovered broader packet stays aligned without collapsing the narrower direct-readback handoff into parked-gap or perf-local wording.",
            "Historical broader packet references are omitted here.",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
            "Current direct contents reads for the runtime atomic64 packet are omitted here.",
        )
        cases += _expect_failure(
            root,
            REPO_REALITY_WARNING,
            "EXPECTED_PIN_SELF_TEST_CASES = 20",
            "EXPECTED_PIN_SELF_TEST_CASES = 19",
        )
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
    except Exception as exc:
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REVERSIBLE_DELIVERY_PINS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
