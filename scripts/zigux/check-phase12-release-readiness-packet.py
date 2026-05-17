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
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RAW_GITHUB_COVERAGE_SURVEY_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    RELEASE_READINESS_SURVEY_PATH,
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
    ],
    SCRIPTS_README_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "make -C zigux phase12-validate",
        "the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet and the parked verify-shard-backed libbpf survey packet reviewable from the scripts root",
    ],
    TESTS_README_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "make -C zigux phase12-validate",
        "phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
        "Documentation/zigux/phase12-nvme-pci-slice.md",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "`PHASE12_STATUS=active`",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`scripts/zigux/check-build-only-phase12-surface.py` now matches that shipped support-checker-plus-validate-route reminder too",
        "the broader reviewer-facing reminder family now keeps the absent standalone `scripts/zigux/check-phase12-cross.py` file explicit instead of overstating a cross-checker surface that current `master` does not ship",
        "make -C zigux phase12-validate",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "`PHASE12_STATUS=active`",
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "treat the directly readable build-only checker, release-readiness checker, workflow, and scripts-root README quartet as bounded reminder evidence only",
        "make -C zigux phase12-validate",
        "if that local fallback is also absent, rerun only the shipped Make routes with `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
    ],
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

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(rel_path: str) -> str:
    title = {
        DOCS_README_PATH: "# Zigux Documentation",
        REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
        SCRIPTS_README_PATH: "# scripts/zigux",
        TESTS_README_PATH: "# zigux/tests",
        RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
        RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
    }[rel_path]
    body = "\n".join(f"- {marker}" for marker in REQUIRED_MARKERS[rel_path])
    return f"{title}\n\n{body}\n"


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


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-packet-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / RELEASE_READINESS_SURVEY_PATH).unlink()
        expect_failure(base, f"missing_file:{RELEASE_READINESS_SURVEY_PATH}")

        write_fixture_tree(base)
        remove_marker(base / RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][1])
        expect_failure(
            base,
            f"{RELEASE_READINESS_SURVEY_PATH}:{REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][1]}",
        )

        write_fixture_tree(base)
        remove_marker(base / RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][2])
        expect_failure(
            base,
            f"{RELEASE_READINESS_SURVEY_PATH}:{REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][2]}",
        )

        write_fixture_tree(base)
        remove_marker(base / RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][3])
        expect_failure(
            base,
            f"{RELEASE_READINESS_SURVEY_PATH}:{REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][3]}",
        )

        write_fixture_tree(base)
        remove_marker(base / RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][2])
        expect_failure(
            base,
            f"{RAW_GITHUB_COVERAGE_SURVEY_PATH}:{REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][2]}",
        )

        write_fixture_tree(base)
        remove_marker(base / RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][4])
        expect_failure(
            base,
            f"{RAW_GITHUB_COVERAGE_SURVEY_PATH}:{REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][4]}",
        )

        write_fixture_tree(base)
        remove_marker(base / SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][0])
        expect_failure(base, f"{SCRIPTS_README_PATH}:{REQUIRED_MARKERS[SCRIPTS_README_PATH][0]}")

        write_fixture_tree(base)
        remove_marker(base / TESTS_README_PATH, REQUIRED_MARKERS[TESTS_README_PATH][2])
        expect_failure(base, f"{TESTS_README_PATH}:{REQUIRED_MARKERS[TESTS_README_PATH][2]}")

        write_fixture_tree(base)
        remove_marker(base / REVIEW_CHECKLIST_PATH, REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][2])
        expect_failure(
            base,
            f"{REVIEW_CHECKLIST_PATH}:{REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][2]}",
        )

        write_fixture_tree(base)
        remove_marker(base / DOCS_README_PATH, REQUIRED_MARKERS[DOCS_README_PATH][4])
        expect_failure(base, f"{DOCS_README_PATH}:{REQUIRED_MARKERS[DOCS_README_PATH][4]}")

        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=10")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the narrow shared Phase 12 release-readiness reminder packet "
            "across the release-readiness survey, raw-coverage warning, docs root, "
            "scripts root, tests root, and review checklist."
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