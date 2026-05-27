#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-coordination-matrix.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
LIBBPF_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
CROSS_COMPILE_SMOKE_PATH = "Documentation/zigux/phase12-cross-compile-smoke.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
CROSS_COMPILE_SMOKE_CHECKER_PATH = "scripts/zigux/check-phase12-cross-compile-smoke.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    COORDINATION_MATRIX_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
    RELEASE_CLOSURE_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    COMPLEX_DRIVER_LANE_PATH,
    LIBBPF_LANE_PATH,
    CROSS_COMPILE_SMOKE_PATH,
    FREEZE_MAP_PATH,
    BUILD_ONLY_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    CROSS_COMPILE_SMOKE_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "compile-smoke checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`",
        "shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`",
        "The active shared build packet is the returned six-file `virtio_net` sextet only:",
        "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
        "`zigux/tests/phase12_virtio_net_receive_refill_replay.zig`",
        "`zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
        "`zigux/tests/phase12_virtio_net_post_reset_replay.zig`",
        "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
        "`zigux/tests/phase12_virtio_net_survey.zig`",
        "`zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
        "Current `master` now ships the degraded-workflow evidence packet `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and `scripts/zigux/validate-phase12.py` while also shipping the `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper set.",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
        "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
        "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    ],
    RELEASE_READINESS_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    ],
    RELEASE_CLOSURE_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence.",
        "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
        "the directly readable `zigux/Makefile` blob `4d572bfda15dc6ae7cd419cc4c7f858d973cda26` still prefers the repo-local `.zig-toolchain` executable",
        "before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
    ],
    COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`",
        "The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through the shared `smoke` and `test` steps",
    ],
    LIBBPF_LANE_PATH: [
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`",
        "The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint",
    ],
    CROSS_COMPILE_SMOKE_PATH: [
        "- support checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`",
        "the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`",
        "current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, and `make -C zigux phase12-virtio-net-syntax-lab-test`",
        "the isolated syntax-lab rerun handles are `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all` and `make -C zigux phase12-virtio-net-syntax-lab-test`, so the companion stays reviewable without joining the shared packet",
        "the shipped cross-compile checker now keeps that returned wrapper wording plus the isolated syntax-lab rerun hook fail-closed across this note and `zigux/Makefile`",
    ],
    FREEZE_MAP_PATH: [
        "- `net/core/skbuff.c`",
        "- `kernel/workqueue.c`",
        "- `kernel/trace/ring_buffer.c`",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        "\"phase12_virtio_net_queue_resume.zig\"",
        "\"phase12_virtio_net_receive_refill_replay.zig\"",
        "\"phase12_virtio_net_transmit_recycle.zig\"",
        "\"phase12_virtio_net_post_reset_replay.zig\"",
        "\"phase12_virtio_net_throughput_parity.zig\"",
        "\"phase12_virtio_net_survey.zig\"",
        "\"phase12-virtio-net-survey-tests\"",
        "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
        "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
        "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "test_step.dependOn(&run_virtio_net_survey_tests.step);",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 smoke packet",
        "run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "run: make -C zigux phase12-test",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ],
}

FORBIDDEN_MARKERS = {
    COORDINATION_MATRIX_PATH: [
        "reminder-only wrapper name `make -C zigux phase12-validate`",
        "still omitting `phase12-validate`",
        "returned five-file `virtio_net` quintet",
    ],
    MAKEFILE_PATH: [
        "phase12: phase12-smoke phase12-test",
    ],
}

EXACT_LINE_MARKER_PATHS = {WORKFLOW_PATH}


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return marker in [line.lstrip() for line in text.splitlines()]
    return marker in text


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
            if not has_required_marker(rel_path, text, marker):
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
            COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_READINESS_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_CLOSURE_PATH: "# Phase 12 Release Closure Checklist",
            RAW_GITHUB_COVERAGE_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex Driver Lane Sequencing",
            LIBBPF_LANE_PATH: "# Phase 12 Libbpf Heavy Consumer Lane Sequencing",
            CROSS_COMPILE_SMOKE_PATH: "# Phase 12 Cross Compile Smoke",
            FREEZE_MAP_PATH: "# Zigux Freeze Map",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {MAKEFILE_PATH, PHASE12_BUILD_PATH, WORKFLOW_PATH}:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    return "# Fixture\n"


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
        updated = text.replace(marker, "", 1)
    if updated == text:
        raise SystemExit(f"unable to remove marker: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-coordination-matrix-"))
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

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
            )
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass")
        print(
            "PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST_CASE_COUNT="
            f"{case_count}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 release coordination matrix against the "
            "shared PMO packet, returned validator-first wrapper set, bounded "
            "compile-smoke companion, and bounded driver-family coordination wording."
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
            print(f"PHASE12_RELEASE_COORDINATION_MATRIX=fail:{failure}")
        return 1

    print("PHASE12_RELEASE_COORDINATION_MATRIX=pass")
    print(
        "PHASE12_RELEASE_COORDINATION_MATRIX_SCOPE="
        "phase12_release_coordination_and_compile_smoke_truth"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
