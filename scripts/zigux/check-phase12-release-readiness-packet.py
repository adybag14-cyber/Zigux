#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-readiness-survey.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RELEASE_COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RAW_GITHUB_COVERAGE_SURVEY_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
        "make -C zigux phase12-validate",
        "scripts/zigux/validate-phase12.py",
        "support material inside that shipped `phase12-validate` route rather than standalone proof of broader driver delivery",
    ],
    REVIEW_CHECKLIST_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "make -C zigux phase12-validate",
        "avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay",
        "support-bundle evidence rather than as a second direct replay route",
        "if `zig` is unavailable on `PATH`, keep the repo-local `.zig-toolchain` fallback plus the attached-Zig degraded rerun explicit by naming `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of implying a focused libbpf-only replay, a cross-build replay, or another unshipped support route?",
    ],
    FREEZE_MAP_PATH: [
        "`net/core/skbuff.c`",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate summary, and rollback owner in the reviewable record for that lane",
    ],
    SCRIPTS_README_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "make -C zigux phase12-validate",
        "the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet and the parked verify-shard-backed libbpf survey packet reviewable from the scripts root",
        "keep the bounded driver-local NVMe foothold explicit too: `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` remain the bounded driver-local packet outside the shared smoke-first route",
        "If `zig` is unavailable on `PATH`, rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`, so the shipped validator-first support bundle stays ahead of the smoke-first reruns.",
    ],
    TESTS_README_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "make -C zigux phase12-validate",
        "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
        "Documentation/zigux/phase12-nvme-pci-slice.md",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "`PHASE12_STATUS=active`",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The route story is the real PMO drift on current `master`: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, but current `zigux/Makefile` no longer provides a shared `phase12-validate`, `phase12-smoke`, or `phase12` wrapper route.",
        "That means the PMO release notes must treat those route names as stale reminder text until same-lane work rematerializes them, rather than presenting them as shipped current-`master` evidence.",
        "make -C zigux phase12-validate",
    ],
    RELEASE_SEQUENCING_PATH: [
        "`PHASE12_STATUS=active`",
        "readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "Current `master` now also ships the degraded-workflow `make -C zigux phase12-validate` route together with `scripts/zigux/validate-phase12.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`, but there is still no focused libbpf-only replay or cross-build replay on current `master`, so this sequencing note must keep that validator-first support packet ahead of the smoke-first direct replay order instead of treating it as broader driver delivery evidence by itself.",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`",
        "Do not invent a focused libbpf-only replay, a cross-build replay, or another unshipped closure route while using the degraded path.",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`",
        "Current `master` now ships the degraded-workflow bundle `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`",
        "The older reminder-only follow-through is now closed on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already keep the shipped `phase12-validate` support bundle, dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard, and attached-Zig degraded rerun order explicit without promoting a standalone cross-build or focused-libbpf replay route.",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.",
    ],
}

REQUIRED_EXACT_COUNT_MARKERS = {
    RELEASE_READINESS_SURVEY_PATH: {
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`": 1,
    },
    RELEASE_SEQUENCING_PATH: {
        "readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`": 1,
    },
    REVIEW_CHECKLIST_PATH: {
        "if `zig` is unavailable on `PATH`, keep the repo-local `.zig-toolchain` fallback plus the attached-Zig degraded rerun explicit by naming `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of implying a focused libbpf-only replay, a cross-build replay, or another unshipped support route?": 1,
    },
    SCRIPTS_README_PATH: {
        "scripts/zigux/check-phase12-release-readiness-packet.py --self-test": 1,
        "If `zig` is unavailable on `PATH`, rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`, so the shipped validator-first support bundle stays ahead of the smoke-first reruns.": 1,
    },
    TESTS_README_PATH: {
        "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`": 1,
        "`Documentation/zigux/phase12-release-coordination-matrix.md`": 1,
    },
    RELEASE_COORDINATION_MATRIX_PATH: {
        "The older reminder-only follow-through is now closed on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already keep the shipped `phase12-validate` support bundle, dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard, and attached-Zig degraded rerun order explicit without promoting a standalone cross-build or focused-libbpf replay route.": 1,
    },
    RAW_GITHUB_COVERAGE_SURVEY_PATH: {
        "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.": 1,
    },
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel_path}:{marker}")
        for marker, expected in REQUIRED_EXACT_COUNT_MARKERS.get(rel_path, {}).items():
            actual = text.count(marker)
            if actual not in (0, expected):
                failures.append(
                    f"{rel_path}:count:{marker}:expected={expected}:actual={actual}"
                )

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(rel_path: str) -> str:
    title = {
        DOCS_README_PATH: "# Zigux Documentation",
        REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
        FREEZE_MAP_PATH: "# Zigux Freeze Map",
        SCRIPTS_README_PATH: "# scripts/zigux",
        TESTS_README_PATH: "# zigux/tests",
        RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
        RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
        RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
        RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
        RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
    }[rel_path]
    body = "\n".join(f"- {marker}" for marker in REQUIRED_MARKERS[rel_path])
    return f"{title}\n\n{body}\n"


def build_self_test_cases() -> list[tuple[str, int]]:
    cases: list[tuple[str, int]] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        fixture_text = marker_fixture(rel_path)
        for marker_index, marker in enumerate(markers):
            if fixture_text.count(marker) == 1:
                cases.append((rel_path, marker_index))
    return cases


def build_exact_count_self_test_cases() -> list[tuple[str, str]]:
    cases: list[tuple[str, str]] = []
    for rel_path, markers in REQUIRED_EXACT_COUNT_MARKERS.items():
        for marker in markers:
            cases.append((rel_path, marker))
    return cases


SELF_TEST_CASES = build_self_test_cases()
EXACT_COUNT_SELF_TEST_CASES = build_exact_count_self_test_cases()
EXPECTED_SELF_TEST_CASE_COUNT = 58


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, marker_fixture(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    path.write_text(
        path.read_text(encoding="utf-8").replace(f"- {marker}\n", "", 1),
        encoding="utf-8",
    )


def duplicate_marker(path: Path, marker: str) -> None:
    path.write_text(
        path.read_text(encoding="utf-8") + f"- {marker}\n",
        encoding="utf-8",
    )


def expect_marker_failure(root: Path, rel_path: str, marker_index: int) -> None:
    marker = REQUIRED_MARKERS[rel_path][marker_index]
    write_fixture_tree(root)
    remove_marker(root / rel_path, marker)
    expect_failure(root, f"{rel_path}:{marker}")


def expect_exact_count_failure(root: Path, rel_path: str, marker: str) -> None:
    write_fixture_tree(root)
    duplicate_marker(root / rel_path, marker)
    expect_failure(root, f"{rel_path}:count:{marker}:expected=1:actual=2")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-packet-"))
    try:
        actual_case_count = (
            len(REQUIRED_FILES) + len(SELF_TEST_CASES) + len(EXACT_COUNT_SELF_TEST_CASES)
        )
        if actual_case_count != EXPECTED_SELF_TEST_CASE_COUNT:
            raise SystemExit(
                "unexpected self-test case count: "
                f"{actual_case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
            )

        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        for rel_path, marker_index in SELF_TEST_CASES:
            expect_marker_failure(base, rel_path, marker_index)

        for rel_path, marker in EXACT_COUNT_SELF_TEST_CASES:
            expect_exact_count_failure(base, rel_path, marker)

        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(
            "PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT="
            f"{actual_case_count}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the narrow shared Phase 12 release-readiness reminder packet "
            "across the release-readiness survey, release-sequencing note, "
            "release-closure checklist, release-coordination matrix, raw-coverage "
            "warning, docs root, scripts root, tests root, and review checklist."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_RELEASE_READINESS_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_RELEASE_READINESS_PACKET=pass")
    print(f"PHASE12_RELEASE_READINESS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_RELEASE_READINESS_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
