#!/usr/bin/env python3
"""Guard the current broad-surface reminder gap for the Phase 11 shared packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
GAP_NOTE_REL = "Documentation/zigux/phase11-shared-summary-gap.md"
CHECKER_REL = "scripts/zigux/check-phase11-shared-summary-gap.py"

REQUIRED_FILES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    GAP_NOTE_REL,
    CHECKER_REL,
)

REQUIRED_GAP_NOTE_MARKERS = (
    "`PHASE11_SHARED_SUMMARY_GAP_STATUS=broad_surfaces_still_skip_phase11`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "Treat that omission as a current reminder-surface gap, not as proof that the underlying Phase 11 validator-first packet is missing.",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-focused-direct-build-replays.py`",
    "`scripts/zigux/check-phase11-shared-replay-contract-counts.py`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`",
    "`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
    "`python3 scripts/zigux/check-phase11-shared-summary-gap.py --self-test`",
    "`python3 scripts/zigux/check-phase11-shared-summary-gap.py`",
    "Treat this note as a reminder-surface gap tracker, not as proof that the whole simple-driver tranche is closed.",
    "The next same-lane reminder-surface step is to refresh one of the broad shared summaries and then narrow or retire this gap note in the same pass.",
)

FORBIDDEN_DOCS_README_MARKERS = (
    "phase11-driver-lane-sequencing.md",
    "check-phase11-build-inventory.py",
    "make -C zigux phase11-validate",
)

FORBIDDEN_REVIEW_CHECKLIST_MARKERS = (
    "shared Phase 11 simple-driver packet",
    "check-phase11-build-inventory.py",
    "check-phase11-shared-replay-contract-counts.py",
)

FORBIDDEN_SCRIPTS_README_MARKERS = (
    "## Phase 11",
    "check-phase11-build-inventory.py",
    "make -C zigux phase11-validate",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def forbid_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckError(f"unexpected marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            raise CheckError(f"missing required file: {rel}")

    gap_note = read_text(root, GAP_NOTE_REL)
    docs_readme = read_text(root, DOCS_README_REL)
    review_checklist = read_text(root, REVIEW_CHECKLIST_REL)
    scripts_readme = read_text(root, SCRIPTS_README_REL)

    require_markers(gap_note, REQUIRED_GAP_NOTE_MARKERS, GAP_NOTE_REL)
    forbid_markers(docs_readme, FORBIDDEN_DOCS_README_MARKERS, DOCS_README_REL)
    forbid_markers(review_checklist, FORBIDDEN_REVIEW_CHECKLIST_MARKERS, REVIEW_CHECKLIST_REL)
    forbid_markers(scripts_readme, FORBIDDEN_SCRIPTS_README_MARKERS, SCRIPTS_README_REL)


def build_sample_repo(root: Path) -> None:
    write_text(root / CHECKER_REL, "#!/usr/bin/env python3\nprint('sample')\n")
    write_text(root / DOCS_README_REL, "Phase 10 notes stay here.\n")
    write_text(root / REVIEW_CHECKLIST_REL, "* current checklist still names earlier packets only\n")
    write_text(root / SCRIPTS_README_REL, "## Phase 10\nShared scripts reminder only.\n")
    write_text(
        root / GAP_NOTE_REL,
        "\n".join([
            "# Phase 11 Shared Summary Gap",
            "`PHASE11_SHARED_SUMMARY_GAP_STATUS=broad_surfaces_still_skip_phase11`",
            "`Documentation/zigux/README.md`",
            "`Documentation/zigux/review-checklist.md`",
            "`scripts/zigux/README.md`",
            "Treat that omission as a current reminder-surface gap, not as proof that the underlying Phase 11 validator-first packet is missing.",
            "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
            "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
            "`Documentation/zigux/phase11-shared-replay-contract.md`",
            "`Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`",
            "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
            "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
            "`zigux/tests/README.md`",
            "`scripts/zigux/check-phase11-build-inventory.py`",
            "`scripts/zigux/check-phase11-focused-direct-build-replays.py`",
            "`scripts/zigux/check-phase11-shared-replay-contract-counts.py`",
            "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
            "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
            "`scripts/zigux/check-phase11-header-boundary-packet.py`",
            "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
            "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
            "`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`",
            "`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
            "`scripts/zigux/validate-phase11.py`",
            "`zigux/Makefile`",
            "`make -C zigux phase11-validate`",
            "`python3 scripts/zigux/check-phase11-shared-summary-gap.py --self-test`",
            "`python3 scripts/zigux/check-phase11-shared-summary-gap.py`",
            "Treat this note as a reminder-surface gap tracker, not as proof that the whole simple-driver tranche is closed.",
            "The next same-lane reminder-surface step is to refresh one of the broad shared summaries and then narrow or retire this gap note in the same pass.",
        ]) + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11_shared_summary_gap_") as tmp:
        root = Path(tmp)
        build_sample_repo(root)
        run_check(root)
        case_count += 1

        (root / GAP_NOTE_REL).write_text("broken\n", encoding="utf-8")
        expect_failure(root, "missing marker in Documentation/zigux/phase11-shared-summary-gap.md: `PHASE11_SHARED_SUMMARY_GAP_STATUS=broad_surfaces_still_skip_phase11`")
        case_count += 1

        build_sample_repo(root)
        write_text(root / DOCS_README_REL, "phase11-driver-lane-sequencing.md\n")
        expect_failure(root, "unexpected marker in Documentation/zigux/README.md: phase11-driver-lane-sequencing.md")
        case_count += 1

        build_sample_repo(root)
        write_text(root / REVIEW_CHECKLIST_REL, "shared Phase 11 simple-driver packet\n")
        expect_failure(root, "unexpected marker in Documentation/zigux/review-checklist.md: shared Phase 11 simple-driver packet")
        case_count += 1

        build_sampleRepo = build_sample_repo
        build_sampleRepo(root)
        write_text(root / SCRIPTS_README_REL, "## Phase 11\n")
        expect_failure(root, "unexpected marker in scripts/zigux/README.md: ## Phase 11")
        case_count += 1

    print("PHASE11_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    print(f"PHASE11_SHARED_SUMMARY_GAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print("PHASE11_SHARED_SUMMARY_GAP=fail")
        print(exc)
        return 1

    print("PHASE11_SHARED_SUMMARY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
