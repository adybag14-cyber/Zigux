#!/usr/bin/env python3
"""Guard the current-head Phase 4 reversible-delivery repo-reality packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
DOCS_README = Path("Documentation/zigux/README.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
SELF = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")
PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")
SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
WORKFLOW_ROUTE_CHECKER = Path("scripts/zigux/check-phase4-workflow-route-counts.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
ATOMIC64_DIFF = Path("zigux/tests/atomic64_diff.zig")
RUNTIME_ATOMIC64_DIFF = Path("zigux/tests/runtime_atomic64_diff.zig")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")
GATE_EVIDENCE = Path("Documentation/zigux/phase4-gate-evidence.md")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")

EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 22
EXPECTED_PIN_SELF_TEST_CASES = 18

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

RECOVERED_NOTE_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-validation-lane-sequencing.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
)

REMAINING_GAP_PACKET = (
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
)

ATOMIC64_DIRECT_PACKET = (
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
)

NOTE_REQ = (
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`.",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    "current-head direct-readback proof that `scripts/zigux/validate-phase4.py` is present again on `master`",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, the directly returned validator, and the still-public-raw-returned build and bitmap replay companions, while exact blob-pin refresh for that broader packet remains the remaining authenticated-readback gap in this handoff.",
)

TESTS_README_PHASE4_REQ = (
    "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current `master` keeps the shared Phase 4 rollback packet narrower than full exact-blob refresh rather than absent: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still need fresh authenticated blob capture in this runtime, but current public raw fallback rereads return those files on `master`",
    "while `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` are directly readable roadmap-backed differential-gate evidence again",
    "Keep the shared ownership reminder truthful by pointing back to `Documentation/zigux/phase4-reversible-delivery-evidence.md` for the narrower current-head handoff instead of reconstructing the broader validator-and-bitmap packet from older route names alone.",
)

CHECKLIST_PHASE4_REQ = (
    "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?",
)

SCRIPTS_README_PHASE4_REQ = (
    "- Phase 4 flow - the current scripts-root artifact-diff and repo-reality packet stays reviewable through the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair instead of reconstructing the validator, build, and bitmap replay companions from older route names alone",
    "- `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "- current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`, so keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending",
)

REQUIRED_FILES = (
    NOTE,
    DOCS_README,
    CHECKLIST,
    TESTS_README,
    SCRIPTS_README,
    SELF,
    PINS,
    PERF_BASELINE_CHECKER,
    PERF_MANIFEST,
    PERF_SURVEY,
    GATE_EVIDENCE,
    MATRIX,
    SEQUENCING_NOTE,
    WORKFLOW_ROUTE_CHECKER,
    MAKEFILE,
    WORKFLOW,
    ATOMIC64_DIFF,
    RUNTIME_ATOMIC64_DIFF,
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


def require(text: str, parts: tuple[str, ...], label: str) -> None:
    missing = [part for part in parts if part not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    missing_files = [rel.as_posix() for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        raise RuntimeError("missing required file: " + ", ".join(missing_files))
    require(read(root, NOTE), NOTE_REQ + DIRECT_READBACK_PACKET + RECOVERED_NOTE_PACKET + REMAINING_GAP_PACKET + ATOMIC64_DIRECT_PACKET, NOTE.as_posix())
    require(read(root, TESTS_README), TESTS_README_PHASE4_REQ, TESTS_README.as_posix())
    require(read(root, CHECKLIST), CHECKLIST_PHASE4_REQ, CHECKLIST.as_posix())
    require(read(root, SCRIPTS_README), SCRIPTS_README_PHASE4_REQ, SCRIPTS_README.as_posix())


def _baseline_note() -> str:
    return "\n".join([
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
        "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`",
        "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
        "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`.",
        "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
        "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here.",
        "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head direct-readback proof that `scripts/zigux/validate-phase4.py` is present again on `master`.",
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`.",
        "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, the directly returned validator, and the still-public-raw-returned build and bitmap replay companions, while exact blob-pin refresh for that broader packet remains the remaining authenticated-readback gap in this handoff.",
        *DIRECT_READBACK_PACKET,
        *RECOVERED_NOTE_PACKET,
        *REMAINING_GAP_PACKET,
        *ATOMIC64_DIRECT_PACKET,
    ]) + "\n"


def _baseline_tests_readme() -> str:
    return "\n".join(TESTS_README_PHASE4_REQ) + "\n"


def _baseline_checklist() -> str:
    return "\n".join(CHECKLIST_PHASE4_REQ) + "\n"


def _baseline_scripts_readme() -> str:
    return "\n".join(SCRIPTS_README_PHASE4_REQ) + "\n"


def _baseline_other(path: Path) -> str:
    return f"placeholder for {path.as_posix()}\n"


def _build_baseline_tree(root: Path) -> None:
    write(root, NOTE, _baseline_note())
    write(root, TESTS_README, _baseline_tests_readme())
    write(root, CHECKLIST, _baseline_checklist())
    write(root, SCRIPTS_README, _baseline_scripts_readme())
    for rel in REQUIRED_FILES:
        if rel in {NOTE, TESTS_README, CHECKLIST, SCRIPTS_README}:
            continue
        write(root, rel, _baseline_other(rel))


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
    with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
        root = Path(tmp)
        _build_baseline_tree(root)
        check(root)
        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=22`\n",
            "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=21`\n",
        )
        cases += _expect_failure(
            root,
            NOTE,
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`\n",
            "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=17`\n",
        )
        cases += _expect_failure(root, NOTE, "Current direct readback in this run confirmed this note", "Current direct readback drifted")
        cases += _expect_failure(root, NOTE, "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair", "Atomic64 packet drifted")
        cases += _expect_failure(root, NOTE, "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`", "Recovered packet drifted")
        cases += _expect_failure(root, NOTE, "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.", "The broader packet is still absent.")
        cases += _expect_failure(root, NOTE, "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:", "The provenance wording drifted:")
        cases += _expect_failure(root, NOTE, "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower:", "The follow-up wording drifted:")
        cases += _expect_failure(root, TESTS_README, TESTS_README_PHASE4_REQ[1], "tests readme drift")
        cases += _expect_failure(root, TESTS_README, TESTS_README_PHASE4_REQ[2], "tests readme split drift")
        cases += _expect_failure(root, CHECKLIST, CHECKLIST_PHASE4_REQ[3], "checklist drift")
        cases += _expect_failure(root, CHECKLIST, CHECKLIST_PHASE4_REQ[4], "checklist atomic drift")
        cases += _expect_failure(root, SCRIPTS_README, SCRIPTS_README_PHASE4_REQ[0], "scripts readme drift")
        cases += _expect_failure(root, SCRIPTS_README, SCRIPTS_README_PHASE4_REQ[2], "scripts split drift")
        cases += _expect_failure(root, PERF_BASELINE_CHECKER, None, None)
        cases += _expect_failure(root, PERF_MANIFEST, None, None)
        cases += _expect_failure(root, PERF_SURVEY, None, None)
        cases += _expect_failure(root, GATE_EVIDENCE, None, None)
        cases += _expect_failure(root, MATRIX, None, None)
        cases += _expect_failure(root, MAKEFILE, None, None)
        cases += _expect_failure(root, WORKFLOW, None, None)
        cases += _expect_failure(root, ATOMIC64_DIFF, None, None)
    if cases != EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES:
        print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=fail")
        print(f"expected {EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES} self-test cases, saw {cases}")
        return 1
    print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass")
    print(f"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        check(args.root.resolve())
    except Exception as exc:
        print(f"PHASE4_REPO_REALITY_WARNING=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REPO_REALITY_WARNING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
