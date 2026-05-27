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
        if (candidate / "Documentation/zigux/phase12-release-sequencing.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    SCRIPTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

VIRTIO_NET_SEXTET = [
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "- `Documentation/zigux/phase12-release-sequencing.md`",
        "- `Documentation/zigux/phase12-release-readiness-survey.md`",
        "- `Documentation/zigux/phase12-release-closure-checklist.md`",
        "- `Documentation/zigux/phase12-release-coordination-matrix.md`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`",
        "`Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`",
    ],
    RELEASE_SEQUENCING_PATH: [
        "shared wrapper evidence on current `master`: `make -C zigux phase12-validate`",
        "shared wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
        "shared wrapper evidence on current `master`: `make -C zigux phase12-test`",
        "shared wrapper evidence on current `master`: `make -C zigux phase12`",
        "The active smoke-first direct shard set on current `master` is",
        "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "- shared-summary lane owner: `pmo-release`",
        "- validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "- shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`",
        "The active shared build packet is the returned six-file `virtio_net` sextet only:",
        "`zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "- lane owner: `pmo-release`",
        "The directly readable validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`",
        "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
        "The current driver-local `virtio_scsi` split must stay explicit too: current `master` keeps the dedicated `Documentation/zigux/phase12-virtio-scsi-slice.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` pair together with `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "- current contents-bridge shared support bundle during degraded contents reads:",
        "- `zigux/tests/phase12_build.zig`",
        "- `scripts/zigux/check-build-only-phase12-surface.py`",
        "- `zigux/Makefile`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared Phase 12 packet",
    ],
    VALIDATOR_PATH: [
        "BUILD_ONLY_CHECKER_PATH",
        "RELEASE_READINESS_CHECKER_PATH",
        "PHASE12_VALIDATION=pass",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps",
        "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route",
    ],
    PHASE12_BUILD_PATH: VIRTIO_NET_SEXTET,
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
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
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(rel_path: str) -> str:
    markers = REQUIRED_MARKERS.get(rel_path, [])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n" + "\n".join(markers) + "\n"
    if rel_path.endswith(".yml"):
        return "name: zigux-bootstrap\n" + "\n".join(markers) + "\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n" + "\n".join(markers) + "\n"
    title = "# Fixture"
    if rel_path == DOCS_README_PATH:
        title = "# Zigux Documentation"
    elif rel_path == REVIEW_CHECKLIST_PATH:
        title = "# Zigux Review Checklist"
    elif rel_path == RELEASE_SEQUENCING_PATH:
        title = "# Phase 12 Release Sequencing"
    elif rel_path == RELEASE_COORDINATION_MATRIX_PATH:
        title = "# Phase 12 Release Coordination Matrix"
    elif rel_path == RELEASE_CLOSURE_CHECKLIST_PATH:
        title = "# Phase 12 Release Closure Checklist"
    elif rel_path == RAW_GITHUB_COVERAGE_SURVEY_PATH:
        title = "# Phase 12 Raw GitHub Coverage Survey"
    elif rel_path == SCRIPTS_README_PATH:
        title = "# scripts/zigux"
    elif rel_path == TESTS_README_PATH:
        title = "# zigux/tests"
    return title + "\n\n" + "\n".join(markers) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def write_sample_root(root: Path) -> None:
    write_fixture_tree(root)


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker, "__REMOVED_PHASE12_COORD_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-coordination-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases)
        print("PHASE12_RELEASE_COORDINATION_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_COORDINATION_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current narrow Phase 12 release-coordination packet "
            "across the sequencing, coordination, closure, workflow, and tests-root "
            "support surfaces."
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample tree to the given path and exit.",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_RELEASE_COORDINATION_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_RELEASE_COORDINATION_PACKET=pass")
    print(
        "PHASE12_RELEASE_COORDINATION_PACKET_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    print(
        "PHASE12_RELEASE_COORDINATION_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
