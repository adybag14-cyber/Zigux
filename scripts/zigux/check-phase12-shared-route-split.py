#!/usr/bin/env python3
"""Guard the Phase 12 shared-build split from driver-local route drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_SHARED_ROUTE_SPLIT"

NOTE_PATH = Path("Documentation/zigux/phase12-complex-driver-lane-sequencing.md")
VIRTIO_NET_SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-net-survey.md")
NVME_SURVEY_PATH = Path("Documentation/zigux/phase12-nvme-pci-survey.md")
VIRTIO_SCSI_SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-scsi-survey.md")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase12_build_inventory.json")
NVME_BUILD_PATH = Path("zigux/tests/phase12_nvme_pci_build.zig")
VIRTIO_SCSI_BUILD_PATH = Path("zigux/tests/phase12_virtio_scsi_survey_build.zig")

REQUIRED_FILES = (
    NOTE_PATH,
    VIRTIO_NET_SURVEY_PATH,
    NVME_SURVEY_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    BUILD_PATH,
    INVENTORY_PATH,
    NVME_BUILD_PATH,
    VIRTIO_SCSI_BUILD_PATH,
)

TEXT_MARKERS = {
    NOTE_PATH: (
        "split-helper `virtio_net` packet",
        "while leaving it outside the shared smoke-first route.",
    ),
    VIRTIO_NET_SURVEY_PATH: (
        "queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
        "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet",
    ),
    NVME_SURVEY_PATH: (
        "the shared `zigux/tests/phase12_build.zig` route still stays virtio-net-only",
        "the bounded NVMe packet remains driver-local through the dedicated `phase12-nvme-pci-direct-test` route",
        "the dedicated `phase12-nvme-pci-survey-test` route",
    ),
    VIRTIO_SCSI_SURVEY_PATH: (
        "the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route now reruns the rollback-only survey packet directly",
        "the shared `zigux/tests/phase12_build.zig` route still covers only the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests",
    ),
    BUILD_PATH: (
        "phase12_virtio_net_queue_resume.zig",
        "phase12_virtio_net_receive_refill_replay.zig",
        "phase12_virtio_net_transmit_recycle.zig",
        "phase12_virtio_net_post_reset_replay.zig",
        "phase12_virtio_net_throughput_parity.zig",
        "phase12_virtio_net_survey.zig",
        "phase12-virtio-net-throughput-parity",
    ),
    NVME_BUILD_PATH: (
        "phase12-nvme-pci-direct-test",
        "phase12-nvme-pci-verify-test",
        "phase12-nvme-pci-replay-wrapper-test",
    ),
    VIRTIO_SCSI_BUILD_PATH: (
        "phase12-virtio-scsi-survey-tests",
        "rollback-only survey tests",
    ),
}

EXPECTED_BUILD_TEST_NAMES = [
    "phase12-virtio-net-queue-resume-tests",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12-virtio-net-survey-tests",
]

EXPECTED_SHARED_DEP_STEPS = [
    "run_virtio_net_queue_resume_tests",
    "run_virtio_net_transmit_recycle_tests",
    "run_virtio_net_receive_refill_replay_tests",
    "run_virtio_net_post_reset_replay_tests",
    "run_virtio_net_throughput_parity_tests",
    "run_virtio_net_survey_tests",
]


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckFailure(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, relative_path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(root, relative_path)
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{relative_path} missing marker: {marker}")


def check_inventory(root: Path) -> None:
    payload = json.loads(read_text(root, INVENTORY_PATH))
    if payload.get("build_test_names") != EXPECTED_BUILD_TEST_NAMES:
        raise CheckFailure(f"{INVENTORY_PATH} build_test_names drifted")
    if payload.get("shared_smoke_depend_steps") != EXPECTED_SHARED_DEP_STEPS:
        raise CheckFailure(f"{INVENTORY_PATH} shared_smoke_depend_steps drifted")
    if payload.get("shared_test_depend_steps") != EXPECTED_SHARED_DEP_STEPS:
        raise CheckFailure(f"{INVENTORY_PATH} shared_test_depend_steps drifted")
    serialized = json.dumps(payload, sort_keys=True)
    if "nvme" in serialized or "virtio_scsi" in serialized:
        raise CheckFailure(f"{INVENTORY_PATH} unexpectedly includes driver-local names")


def check(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"missing required file: {relative_path}")
    for relative_path, markers in TEXT_MARKERS.items():
        require_markers(root, relative_path, markers)
    build_text = read_text(root, BUILD_PATH)
    if "phase12_nvme_pci" in build_text or "phase12_virtio_scsi" in build_text:
        raise CheckFailure(f"{BUILD_PATH} unexpectedly references driver-local routes")
    check_inventory(root)


def write_fixture(root: Path) -> None:
    payload = {
        "build_test_names": EXPECTED_BUILD_TEST_NAMES,
        "shared_smoke_depend_steps": EXPECTED_SHARED_DEP_STEPS,
        "shared_test_depend_steps": EXPECTED_SHARED_DEP_STEPS,
    }
    for relative_path, markers in TEXT_MARKERS.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")
    inventory_path = root / INVENTORY_PATH
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-shared-route-split-") as tmp:
        root = Path(tmp)
        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure:
            cases += 1
        else:
            raise AssertionError("expected build marker failure")

        write_fixture(root)
        payload = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
        payload["build_test_names"].append("phase12-nvme-pci-direct-tests")
        (root / INVENTORY_PATH).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure:
            cases += 1
        else:
            raise AssertionError("expected inventory drift failure")

        write_fixture(root)
        (root / NVME_SURVEY_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure:
            cases += 1
        else:
            raise AssertionError("expected nvme marker failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check(args.root)
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail:{exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
