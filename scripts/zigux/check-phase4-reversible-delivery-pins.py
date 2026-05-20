#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery repo-reality handoff."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
LEGACY_PIN_SELF_TEST_CASES_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22
EXPECTED_PIN_SELF_TEST_CASES = 18

EXPECTED_SHA_LINES = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=443b0528b16c6d6441a488062d5b9ae5bf66cb84`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=31f1d2ba21c371180593c9ad6de45b1fba0e04be`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=2cbbb20bda78b380e6fa9884f6043d140782be4a`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=e76e1ccb4c7605b55b752aa00d7a8e61e99bc5ec`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA=c294a84d1eea361d2438313c8daf0d0a80ae1bc6`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA=131c6315fc23f72576f0a60b2cb7ff1b6b59f492`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=b7cad25fa9e79127941335dda93b7d86dcafecf3`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=065a43cd4984f898207e5a9a3ff9434ecaa2adca`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=984085b3db4de17e86646b0c1463ee6224bd8efc`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA=dea77e6385618147aba44d3714f73b6c5249e942`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=7f0f4cab8042ae95cb52834691a2ffac7a847a6a`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=a4aad5b4904fb2d68f63921dc7693eea94f80780`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=a28a7393df1b270de8c80c57c30287d548bd0c4e`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=fa4ab6b736a3eba358630a9913b447f77569ab29`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=271848a2839e3fd818a6492537fbc6af7f195063`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=d3c784734232d35d744ca5d2a0ea2ea2580524c7`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=a1629d16cbee12a163e71aeb862368764260ecf9`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=75c533b819a0bb422e69c92a33a23da7c04d5af1`",
)

NOTE_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
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


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    warning = read(root, REPO_REALITY_WARNING)
    require(note, EXPECTED_SHA_LINES + NOTE_MARKERS, NOTE.as_posix())
    require(warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())


def _baseline_note() -> str:
    return "\n".join([
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "## Status",
        *EXPECTED_SHA_LINES,
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
        "",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here.",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    ]) + "\n"


def _baseline_warning() -> str:
    return "\n".join([
        "#!/usr/bin/env python3",
        "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22",
        "EXPECTED_PIN_SELF_TEST_CASES = 18",
        "scripts/zigux/check-phase4-reversible-delivery-pins.py",
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    ]) + "\n"


def _build_baseline_tree(root: Path) -> None:
    write(root, NOTE, _baseline_note())
    write(root, REPO_REALITY_WARNING, _baseline_warning())


def _expect_failure(root: Path, rel: Path, old: str, new: str) -> int:
    _build_baseline_tree(root)
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
        for line in EXPECTED_SHA_LINES[:12]:
            cases += _expect_failure(root, NOTE, line, line.replace(line[-41:-1], "0" * 40))
        cases += _expect_failure(root, NOTE, "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`", "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=21`")
        cases += _expect_failure(root, NOTE, "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`", "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=17`")
        cases += _expect_failure(root, NOTE, "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:", "The provenance wording drifted:")
        cases += _expect_failure(root, REPO_REALITY_WARNING, "EXPECTED_PIN_SELF_TEST_CASES = 18", "EXPECTED_PIN_SELF_TEST_CASES = 17")
        cases += _expect_failure(root, REPO_REALITY_WARNING, "scripts/zigux/check-phase4-perf-baseline-packet.py", "scripts/zigux/check-phase4-perf-packet.py")
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
