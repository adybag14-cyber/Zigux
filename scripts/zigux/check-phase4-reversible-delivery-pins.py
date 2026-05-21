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
DOCS_README = Path("Documentation/zigux/README.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
LEGACY_PIN_SELF_TEST_CASES_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22
EXPECTED_PIN_SELF_TEST_CASES = 18

STATIC_SHA_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=5d125f0e20b3378b2d5ff1b94d0779557a980cee`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=ffe579365d4cf0cca43f8840f917be0623e3b49b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=f2e40cc9cc3836dbf83b918ab680bb0c71de113b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA=847d8af2cb90a9669112183dd6197322c7ab10bd`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=667d5ca6057cc391c6f05227997542b59d3c52b6`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=6e4f3a7b3d9c2da125d80d84ac3ce2fb886fd985`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=8ac70b09fb17b97f0c067547f2ad8b3855c4a908`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=75c533b819a0bb422e69c92a33a23da7c04d5af1`",
)
CURRENT_HEAD_BLOB_PINS = (
    ("PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA", REPO_REALITY_WARNING),
    ("PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA", CHECKLIST),
    ("PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA", TESTS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA", DOCS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA", SCRIPTS_README),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA", PERF_BASELINE_CHECKER),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA", PERF_MANIFEST),
    ("PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA", PERF_SURVEY),
)
EXPECTED_STATUS_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
)
EXPECTED_PACKET_MEMBER_LINES = (
    "Current direct-readback packet members:",
    "  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "  * `Documentation/zigux/README.md`",
    "  * `Documentation/zigux/review-checklist.md`",
    "  * `zigux/tests/README.md`",
    "  * `scripts/zigux/README.md`",
    "  * `scripts/zigux/check-phase4-repo-reality-warning.py`",
    "  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)
EXPECTED_RECOVERY_MARKERS = (
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
)
NOTE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
)

WARNING_MARKERS = (
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22",
    "EXPECTED_PIN_SELF_TEST_CASES = 18",
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


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def current_head_blob_pin_line(root: Path, label: str, rel: Path) -> str:
    return f"  * `{label}={git_blob_sha(root / rel)}`"


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
    require(note, STATIC_SHA_LINES + EXPECTED_STATUS_LINES + NOTE_MARKERS + EXPECTED_PACKET_MEMBER_LINES + EXPECTED_RECOVERY_MARKERS, NOTE.as_posix())
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
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "",
        "Current direct-readback packet members:",
        "  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
        "  * `Documentation/zigux/README.md`",
        "  * `Documentation/zigux/review-checklist.md`",
        "  * `zigux/tests/README.md`",
        "  * `scripts/zigux/README.md`",
        "  * `scripts/zigux/check-phase4-repo-reality-warning.py`",
        "  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
        "",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
        "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
        "",
    ]
    return "\n".join(lines) + "\n"


def _baseline_warning() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22",
            "EXPECTED_PIN_SELF_TEST_CASES = 18",
            "scripts/zigux/check-phase4-reversible-delivery-pins.py",
            "scripts/zigux/check-phase4-perf-baseline-packet.py",
            "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
        ]
    ) + "\n"


def _build_baseline_tree(root: Path) -> None:
    required_files = {
        NOTE,
        REPO_REALITY_WARNING,
        DOCS_README,
        CHECKLIST,
        TESTS_README,
        SCRIPTS_README,
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
        cases += 1

        for label, _ in CURRENT_HEAD_BLOB_PINS[:7]:
            _build_baseline_tree(root)
            line = find_status_line(read(root, NOTE), label)
            cases += _expect_failure(root, NOTE, line, line.replace(line[-41:-1], "0" * 40))

        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=21`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=17`",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "Current direct-readback packet members:",
            "Current packet members:",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
            "  * `scripts/zigux/check-phase4-reversible-delivery-guard.py`",
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
            "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.",
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
            NOTE,
            "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
            "The provenance wording drifted:",
        )
        cases += _expect_failure(
            root,
            REPO_REALITY_WARNING,
            "EXPECTED_PIN_SELF_TEST_CASES = 18",
            "EXPECTED_PIN_SELF_TEST_CASES = 17",
        )
        cases += _expect_failure(
            root,
            REPO_REALITY_WARNING,
            "scripts/zigux/check-phase4-perf-baseline-packet.py",
            "scripts/zigux/check-phase4-perf-packet.py",
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
