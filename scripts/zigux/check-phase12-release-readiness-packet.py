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

FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    FREEZE_MAP_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    SCRIPTS_README_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: [
        "still agree that current `zigux/Makefile` ships `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while `make -C zigux phase12-validate` remains reminder-only vocabulary",
        "keep the repo-local `.zig-toolchain` fallback before the attached-Zig degraded rerun order explicit",
        "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The route story on current `master` is split rather than absent: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again, but it still does not provide `phase12-validate`.",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
    ],
    RELEASE_SEQUENCING_PATH: [
        "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
        "Current repo-reality override: `zigux/Makefile` still omits `phase12-validate` on current `master`, but it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again.",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.",
        "the raw-URL-backed fallback pair and the contents-bridge-backed shared support bundle are distinct evidence paths in this runtime",
        "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate` stays reminder-only vocabulary until the wrapper returns on current `master`",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
        "keep the repo-local `.zig-toolchain` then attached-Zig degraded rerun order explicit here too: rely on the Makefile fallback first, then name `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text",
    ],
    VALIDATOR_PATH: [
        "RELEASE_READINESS_CHECKER_PATH",
        "BUILD_ONLY_CHECKER_PATH",
        "make -C zigux phase12-validate",
        "stale reminder vocabulary",
        "scripts-side support packet",
    ],
    MAKEFILE_PATH: [
        "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.",
        "Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
        "Keep the bounded packet split explicit here too: `virtio_net` remains starter-present reviewability, `virtio_scsi` remains the smoke-first and rollback-lab packet",
    ],
    WORKFLOW_PATH: [
        "- name: Run current Phase 12 smoke packet",
        "run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "run: make -C zigux phase12-test",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ]
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
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
            RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {
            VALIDATOR_PATH,
            MAKEFILE_PATH,
        }:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".yml"):
        return "name: zigux-bootstrap\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = [
            FREEZE_MAP_PATH,
            REVIEW_CHECKLIST_PATH,
            RELEASE_READINESS_SURVEY_PATH,
            RELEASE_SEQUENCING_PATH,
            RELEASE_CLOSURE_CHECKLIST_PATH,
            RELEASE_COORDINATION_MATRIX_PATH,
            RAW_GITHUB_COVERAGE_SURVEY_PATH,
            BUILD_ONLY_CHECKER_PATH,
            RELEASE_READINESS_CHECKER_PATH,
            SCRIPTS_README_PATH,
            VALIDATOR_PATH,
            MAKEFILE_PATH,
            TESTS_README_PATH,
            PHASE12_BUILD_PATH,
            WORKFLOW_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (REVIEW_CHECKLIST_PATH, REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][0]),
            (REVIEW_CHECKLIST_PATH, REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][1]),
            (REVIEW_CHECKLIST_PATH, REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][2]),
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][0]),
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][1]),
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][2]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][0]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][1]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][2]),
            (RELEASE_CLOSURE_CHECKLIST_PATH, REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][0]),
            (RELEASE_CLOSURE_CHECKLIST_PATH, REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][1]),
            (RELEASE_CLOSURE_CHECKLIST_PATH, REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][2]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][0]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][1]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][2]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][0]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][1]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][2]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][0]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][1]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][2]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][0]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][1]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][2]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][3]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][4]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][1]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][2]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][3]),
            (TESTS_README_PATH, REQUIRED_MARKERS[TESTS_README_PATH][0]),
            (TESTS_README_PATH, REQUIRED_MARKERS[TESTS_README_PATH][1]),
            (TESTS_README_PATH, REQUIRED_MARKERS[TESTS_README_PATH][2]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][0]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][1]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][2]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][3]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        forbidden_cases = [
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][1]),
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(base / rel_path, (base / rel_path).read_text(encoding="utf-8") + marker + "\n")
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current narrow Phase 12 release-readiness support bundle "
            "around the release notes, shared reminder surfaces, degraded fallback "
            "wording, and shared Makefile routes."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the script directory.",
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
    print(
        "PHASE12_RELEASE_READINESS_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())