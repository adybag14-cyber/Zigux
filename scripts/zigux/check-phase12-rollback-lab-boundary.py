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

READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"

REQUIRED_FILES = [
    READINESS_PATH,
    CLOSURE_PATH,
    MATRIX_PATH,
    PHASE12_BUILD_PATH,
]

REQUIRED_MARKERS = {
    READINESS_PATH: [
        "zigux/tests/phase12_virtio_scsi_survey_build.zig",
        "outside the shared `virtio_net` smoke-and-test route",
        "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
        "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    ],
    CLOSURE_PATH: [
        "zigux/tests/phase12_virtio_scsi_survey_build.zig",
        "drivers/scsi/virtio_scsi.zig",
        "remain absent on current `master`",
        "rather than runtime queue, DMA, recovery, or throughput claims",
    ],
    MATRIX_PATH: [
        "only the six-file `virtio_net` sextet may move through the shared wrapper set",
        "rollback-lab `virtio_scsi` survey-build packet",
        "stay outside that shared route until new checker-backed promotions land on `master`",
    ],
    PHASE12_BUILD_PATH: [
        "phase12_virtio_net_queue_resume.zig",
        "phase12_virtio_net_receive_refill_replay.zig",
        "phase12_virtio_net_transmit_recycle.zig",
        "phase12_virtio_net_post_reset_replay.zig",
        "phase12_virtio_net_throughput_parity.zig",
        "phase12_virtio_net_survey.zig",
    ],
}

FORBIDDEN_BUILD_MARKERS = [
    "phase12_virtio_scsi_survey_build.zig",
    "phase12_virtio_scsi_repeated_replan_gate.zig",
    "phase12_virtio_scsi_repeated_rollback_gate.zig",
    "phase12_virtio_scsi_packet.zig",
]


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

    build_text = (root / PHASE12_BUILD_PATH).read_text(encoding="utf-8")
    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build_text:
            failures.append(f"forbidden_shared_build_marker:{PHASE12_BUILD_PATH}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    titles = {
        READINESS_PATH: "# Phase 12 Release Readiness Survey",
        CLOSURE_PATH: "# Phase 12 Release Closure Checklist",
        MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
        PHASE12_BUILD_PATH: "// phase12 build fixture",
    }
    if rel_path == PHASE12_BUILD_PATH:
        return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    return marker_fixture(titles[rel_path], REQUIRED_MARKERS[rel_path])


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
        updated = text.replace(marker, "__REMOVED_PHASE12_ROLLBACK_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-rollback-lab-boundary-"))
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

        for marker in FORBIDDEN_BUILD_MARKERS:
            write_fixture_tree(base)
            build_path = base / PHASE12_BUILD_PATH
            build_path.write_text(
                build_path.read_text(encoding="utf-8") + f"{marker}\n",
                encoding="utf-8",
            )
            expect_failure(base, f"forbidden_shared_build_marker:{PHASE12_BUILD_PATH}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases) + len(FORBIDDEN_BUILD_MARKERS)
        print("PHASE12_ROLLBACK_LAB_BOUNDARY_SELF_TEST=pass")
        print(f"PHASE12_ROLLBACK_LAB_BOUNDARY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the Phase 12 virtio_scsi rollback-lab survey-build "
            "packet remains documented as adjacent evidence and is not promoted "
            "into the shared phase12 smoke/test build route."
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
            print(f"PHASE12_ROLLBACK_LAB_BOUNDARY=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_ROLLBACK_LAB_BOUNDARY=pass")
    print(f"PHASE12_ROLLBACK_LAB_BOUNDARY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_ROLLBACK_LAB_BOUNDARY_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE12_ROLLBACK_LAB_BOUNDARY_FORBIDDEN_BUILD_MARKER_COUNT="
        f"{len(FORBIDDEN_BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
