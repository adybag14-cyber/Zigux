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
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RELEASE_COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RAW_GITHUB_COVERAGE_SURVEY_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
PHASE12_COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
CROSS_COMPILE_SMOKE_PATH = "Documentation/zigux/phase12-cross-compile-smoke.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
COMPLEX_DRIVER_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-complex-driver-lane-packet.py"
CROSS_COMPILE_SMOKE_CHECKER_PATH = "scripts/zigux/check-phase12-cross-compile-smoke.py"
RELEASE_READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_LANE_MARKER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-lane-marker.py"
LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    DOCS_README_PATH,
    FREEZE_MAP_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH,
    CROSS_COMPILE_SMOKE_PATH,
    SCRIPTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
    COMPLEX_DRIVER_PACKET_CHECKER_PATH,
    CROSS_COMPILE_SMOKE_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    LIBBPF_HEAVY_CONSUMER_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "Phase 12 notes",
        "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "make -C zigux phase12-validate",
    ],
    FREEZE_MAP_PATH: [
        "kernel/workqueue.c",
        "net/core/skbuff.c",
    ],
    REVIEW_CHECKLIST_PATH: [
        "Phase 12 reviewer prompt:",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "scripts/zigux/check-phase12-release-readiness-packet.py",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "scripts/zigux/check-phase12-complex-driver-lane-packet.py",
        "scripts/zigux/check-phase12-cross-compile-smoke.py",
        "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    ],
    RELEASE_SEQUENCING_PATH: [
        "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
        "python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
        "make -C zigux phase12-smoke",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "zigux/tests/phase12_virtio_scsi_survey_build.zig",
        "make -C zigux phase12-test",
        "scripts/zigux/check-phase12-libbpf-lane-marker.py",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "anti-overlap checker: `scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
        "compile-smoke checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`",
        "scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
        "scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
        "current contents-bridge shared support bundle during degraded contents reads:",
        "Segmented rollout is the governing rule for the active tranche: only the six-file `virtio_net` sextet may move through the shared wrapper set, while the rollback-lab `virtio_scsi` survey-build packet, the published-but-unwired `nvme_pci` foothold, and the parked libbpf packet stay outside that shared route until new checker-backed promotions land on `master`.",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "scripts/zigux/check-phase12-complex-driver-lane-packet.py",
        "scripts/zigux/check-build-only-phase12-surface.py",
        "zigux/tests/phase12_build.zig",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "make -C zigux phase12-validate",
        "zigux/tests/phase12_virtio_net_queue_resume.zig",
        "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "make -C zigux phase12-validate",
    ],
    CROSS_COMPILE_SMOKE_PATH: [
        "scripts/zigux/check-phase12-cross-compile-smoke.py",
        "make -C zigux phase12-validate",
    ],
    SCRIPTS_README_PATH: [
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "make -C zigux phase12-smoke",
    ],
    VALIDATOR_PATH: [
        "BUILD_ONLY_CHECKER_PATH = \"scripts/zigux/check-build-only-phase12-surface.py\"",
        "RELEASE_READINESS_CHECKER_PATH = (",
        "PHASE12_VALIDATION=pass",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "scripts/zigux/check-phase12-libbpf-lane-marker.py",
        "zigux/tests/phase12_virtio_scsi_survey_build.zig",
        "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    ],
    WORKFLOW_PATH: [
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "run: python3 scripts/zigux/validate-phase12.py",
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


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    titles = {
        DOCS_README_PATH: "# Zigux Documentation",
        FREEZE_MAP_PATH: "# Zigux Freeze Map",
        REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
        RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
        RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
        RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
        RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
        RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
        PHASE12_COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex-Driver Lane Sequencing",
        PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
        CROSS_COMPILE_SMOKE_PATH: "# Phase 12 Cross-Compile Smoke",
        SCRIPTS_README_PATH: "# scripts/zigux",
        TESTS_README_PATH: "# zigux/tests",
        WORKFLOW_PATH: "name: zigux-bootstrap",
    }
    if rel_path in REQUIRED_MARKERS:
        if rel_path == VALIDATOR_PATH:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        if rel_path == MAKEFILE_PATH:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        if rel_path == WORKFLOW_PATH:
            return "\n".join(f"- name: fixture\n  {marker}" for marker in REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(titles.get(rel_path, "# Fixture"), REQUIRED_MARKERS[rel_path])
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
    if updated == text:
        updated = text.replace(marker, "__REMOVED_PHASE12_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-"))
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
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the narrow Phase 12 release-readiness support bundle around "
            "the shared PMO notes, support checkers, returned wrapper set, and "
            "coordination-matrix exactness."
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
    print("PHASE12_RELEASE_READINESS_PACKET_FORBIDDEN_MARKER_COUNT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
