#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/README.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

TESTS_README_PATH = "zigux/tests/README.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
COMPLEX_DRIVER_LANE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-complex-driver-lane-packet.py"
)
CROSS_COMPILE_SMOKE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-cross-compile-smoke.py"
)
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_LANE_MARKER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-lane-marker.py"
LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = (
    "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
VIRTIO_NET_QUEUE_RESUME_PATH = "zigux/tests/phase12_virtio_net_queue_resume.zig"
VIRTIO_NET_RECEIVE_REFILL_REPLAY_PATH = (
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig"
)
VIRTIO_NET_TRANSMIT_RECYCLE_PATH = (
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig"
)
VIRTIO_NET_POST_RESET_REPLAY_PATH = (
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig"
)
VIRTIO_NET_THROUGHPUT_PARITY_PATH = (
    "zigux/tests/phase12_virtio_net_throughput_parity.zig"
)
VIRTIO_NET_SURVEY_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
VIRTIO_SCSI_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
VIRTIO_SCSI_SURVEY_ZIG_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
VIRTIO_SCSI_SURVEY_BUILD_PATH = "zigux/tests/phase12_virtio_scsi_survey_build.zig"
NVME_SURVEY_PATH = "Documentation/zigux/phase12-nvme-pci-survey.md"
NVME_MANIFEST_PATH = "zigux/tests/phase12_nvme_pci_manifest.json"
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_VERIFY_SHARD_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"

REQUIRED_FILES = [
    TESTS_README_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    COMPLEX_DRIVER_LANE_CHECKER_PATH,
    CROSS_COMPILE_SMOKE_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    LIBBPF_HEAVY_CONSUMER_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    WORKFLOW_PATH,
    VIRTIO_NET_QUEUE_RESUME_PATH,
    VIRTIO_NET_RECEIVE_REFILL_REPLAY_PATH,
    VIRTIO_NET_TRANSMIT_RECYCLE_PATH,
    VIRTIO_NET_POST_RESET_REPLAY_PATH,
    VIRTIO_NET_THROUGHPUT_PARITY_PATH,
    VIRTIO_NET_SURVEY_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    VIRTIO_SCSI_MANIFEST_PATH,
    VIRTIO_SCSI_SURVEY_ZIG_PATH,
    VIRTIO_SCSI_SURVEY_BUILD_PATH,
    NVME_SURVEY_PATH,
    NVME_MANIFEST_PATH,
    LIBBPF_SEGMENT_SURVEY_PATH,
    LIBBPF_VERIFY_SHARD_NOTE_PATH,
    LIBBPF_SNAPSHOT_PATH,
]

REQUIRED_MARKERS = {
    TESTS_README_PATH: [
        "## Phase 12 shared release packet",
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
        "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
        "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
        "Tests-root reviewer prompt:",
    ],
    RELEASE_SEQUENCING_PATH: [
        "`zigux/tests/README.md`",
        "then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO release wording.",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "`zigux/tests/README.md`",
        "The next honest same-lane follow-through is therefore reminder-side only: leave the shared release notes parked unless `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` still understate the directly readable support bundle",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "`zigux/tests/README.md`",
        "The next honest same-lane follow-through is therefore reminder-side only: leave this checklist parked unless `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, or `zigux/tests/README.md` understates the directly readable support bundle",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "`zigux/tests/README.md`",
        "`zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "`zigux/tests/README.md`",
        "`zigux/tests/phase12_build.zig`",
        "`scripts/zigux/check-build-only-phase12-surface.py`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "Phase 12 reviewer prompt:",
        "`zigux/tests/phase12_virtio_scsi_manifest.json`",
        "`zigux/tests/phase12_virtio_scsi_survey.zig`",
        "`zigux/Makefile`",
        "current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again",
    ],
    SCRIPTS_README_PATH: [
        "## Phase 12",
        "`scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    BUILD_PATH: [
        '"phase12_virtio_net_queue_resume.zig"',
        '"phase12_virtio_net_receive_refill_replay.zig"',
        '"phase12_virtio_net_transmit_recycle.zig"',
        '"phase12_virtio_net_post_reset_replay.zig"',
        '"phase12_virtio_net_throughput_parity.zig"',
        '"phase12_virtio_net_survey.zig"',
    ],
    WORKFLOW_PATH: [
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "run: make -C zigux phase12",
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
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
    if rel_path == TESTS_README_PATH:
        return "# zigux/tests\n\n" + "\n".join(REQUIRED_MARKERS[TESTS_README_PATH]) + "\n"
    if rel_path.endswith(".md"):
        markers = REQUIRED_MARKERS.get(rel_path, [])
        title = "# Fixture"
        if rel_path == RELEASE_SEQUENCING_PATH:
            title = "# Phase 12 Release Sequencing"
        elif rel_path == RELEASE_READINESS_SURVEY_PATH:
            title = "# Phase 12 Release Readiness Survey"
        elif rel_path == RELEASE_CLOSURE_CHECKLIST_PATH:
            title = "# Phase 12 Release Closure Checklist"
        elif rel_path == RELEASE_COORDINATION_MATRIX_PATH:
            title = "# Phase 12 Release Coordination Matrix"
        elif rel_path == RAW_GITHUB_COVERAGE_PATH:
            title = "# Phase 12 Raw GitHub Coverage Survey"
        elif rel_path == REVIEW_CHECKLIST_PATH:
            title = "# Zigux Review Checklist"
        elif rel_path == SCRIPTS_README_PATH:
            title = "# scripts/zigux"
        return title + "\n\n" + "\n".join(markers) + "\n"
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith("Makefile"):
        return "\n".join(REQUIRED_MARKERS[MAKEFILE_PATH]) + "\n"
    if rel_path.endswith(".yml"):
        return "\n".join(f"- name: fixture\n  {marker}" for marker in REQUIRED_MARKERS[WORKFLOW_PATH]) + "\n"
    if rel_path.endswith(".zig") or rel_path.endswith(".json"):
        markers = REQUIRED_MARKERS.get(rel_path, [])
        prefix = "// fixture\n" if rel_path.endswith(".zig") else '{ "fixture": true }\n'
        return prefix + ("\n".join(markers) + "\n" if markers else "")
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker, "__REMOVED_MARKER__")
    if updated == text:
        raise SystemExit(f"unable to remove marker: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-tests-readme-alignment-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        cases = 0
        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            missing = validate(base)
            expected = f"missing_file:{rel_path}"
            if expected not in missing:
                raise SystemExit(f"expected {expected!r}, got {missing!r}")
            cases += 1

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                write_fixture_tree(base)
                remove_marker(base / rel_path, marker)
                missing = validate(base)
                expected = f"missing_marker:{rel_path}:{marker}"
                if expected not in missing:
                    raise SystemExit(f"expected {expected!r}, got {missing!r}")
                cases += 1

        print("PHASE12_TESTS_README_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE12_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the shared Phase 12 tests-root release packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=__import__('sys').stderr)
        return 1

    print("PHASE12_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE12_TESTS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_TESTS_README_ALIGNMENT_SHARED_VIRTIO_NET_PACKET_COUNT=6"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
