#!/usr/bin/env python3
"""Fail-closed checker for the Phase 12 shared-build versus dedicated-route split."""

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
BUILD_INVENTORY_PATH = Path("zigux/tests/fixtures/phase12_build_inventory.json")
NVME_BUILD_PATH = Path("zigux/tests/phase12_nvme_pci_build.zig")
VIRTIO_SCSI_SURVEY_BUILD_PATH = Path("zigux/tests/phase12_virtio_scsi_survey_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    NOTE_PATH,
    VIRTIO_NET_SURVEY_PATH,
    NVME_SURVEY_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    BUILD_PATH,
    BUILD_INVENTORY_PATH,
    NVME_BUILD_PATH,
    VIRTIO_SCSI_SURVEY_BUILD_PATH,
    MAKEFILE_PATH,
)

NOTE_MARKERS = (
    "build-only contract reminders, and anti-overlap guidance for the split-helper `virtio_net` packet",
    "`zigux/tests/phase12_build.zig` currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through shared `smoke` and `test`",
    "while leaving it outside the shared smoke-first route.",
)

VIRTIO_NET_SURVEY_MARKERS = (
    "queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
)

NVME_SURVEY_MARKERS = (
    "the shared `zigux/tests/phase12_build.zig` route still stays virtio-net-only",
    "the bounded NVMe packet remains driver-local through the dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig`",
    "and the dedicated `phase12-nvme-pci-survey-test` route in `zigux/tests/phase12_nvme_pci_survey_build.zig`",
)

VIRTIO_SCSI_SURVEY_MARKERS = (
    "the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route now reruns the rollback-only survey packet directly",
    "the shared `zigux/tests/phase12_build.zig` route still covers only the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests",
    "rollback evidence while the driver-local starter and replay gates remain absent",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-throughput-parity",
)

BUILD_COUNT_MARKERS = {
    "b.addTest(.{": 6,
    "smoke_step.dependOn(": 6,
    "test_step.dependOn(": 6,
}

BUILD_FORBIDDEN_MARKERS = (
    "phase12_nvme_pci",
    "phase12_virtio_scsi",
)

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

NVME_BUILD_MARKERS = (
    "phase12-nvme-pci-direct-test",
    "phase12-nvme-pci-verify-test",
    "phase12-nvme-pci-replay-wrapper-test",
)

VIRTIO_SCSI_SURVEY_BUILD_MARKERS = (
    "phase12-virtio-scsi-survey-tests",
    "Run the Phase 12 virtio_scsi rollback-only survey tests",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_counts(text: str, counts: dict[str, int], label: str) -> None:
    for marker, expected_count in counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            raise CheckFailure(
                f"{label} wrong count for {marker!r}: expected {expected_count}, got {actual_count}"
            )


def require_absent(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label} unexpected marker: {marker}")


def load_json(root: Path, relative_path: Path) -> object:
    try:
        return json.loads((root / relative_path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc
    except json.JSONDecodeError as exc:
        raise CheckFailure(f"{relative_path} invalid JSON: {exc}") from exc


def check_inventory(root: Path) -> None:
    payload = load_json(root, BUILD_INVENTORY_PATH)
    if not isinstance(payload, dict):
        raise CheckFailure(f"{BUILD_INVENTORY_PATH} must contain a JSON object")

    build_test_names = payload.get("build_test_names")
    if build_test_names != EXPECTED_BUILD_TEST_NAMES:
        raise CheckFailure(
            f"{BUILD_INVENTORY_PATH} build_test_names drifted: {build_test_names!r}"
        )

    shared_smoke = payload.get("shared_smoke_depend_steps")
    if shared_smoke != EXPECTED_SHARED_DEP_STEPS:
        raise CheckFailure(
            f"{BUILD_INVENTORY_PATH} shared_smoke_depend_steps drifted: {shared_smoke!r}"
        )

    shared_test = payload.get("shared_test_depend_steps")
    if shared_test != EXPECTED_SHARED_DEP_STEPS:
        raise CheckFailure(
            f"{BUILD_INVENTORY_PATH} shared_test_depend_steps drifted: {shared_test!r}"
        )

    serialized = json.dumps(payload, sort_keys=True)
    if "nvme" in serialized or "virtio_scsi" in serialized:
        raise CheckFailure(
            f"{BUILD_INVENTORY_PATH} unexpectedly includes dedicated-route driver names"
        )


def check(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"missing required file: {relative_path}")

    require_markers(read_text(root, NOTE_PATH), NOTE_MARKERS, str(NOTE_PATH))
    require_markers(
        read_text(root, VIRTIO_NET_SURVEY_PATH),
        VIRTIO_NET_SURVEY_MARKERS,
        str(VIRTIO_NET_SURVEY_PATH),
    )
    require_markers(
        read_text(root, NVME_SURVEY_PATH),
        NVME_SURVEY_MARKERS,
        str(NVME_SURVEY_PATH),
    )
    require_markers(
        read_text(root, VIRTIO_SCSI_SURVEY_PATH),
        VIRTIO_SCSI_SURVEY_MARKERS,
        str(VIRTIO_SCSI_SURVEY_PATH),
    )

    build_text = read_text(root, BUILD_PATH)
    require_markers(build_text, BUILD_MARKERS, str(BUILD_PATH))
    require_counts(build_text, BUILD_COUNT_MARKERS, str(BUILD_PATH))
    require_absent(build_text, BUILD_FORBIDDEN_MARKERS, str(BUILD_PATH))

    check_inventory(root)

    require_markers(
        read_text(root, NVME_BUILD_PATH),
        NVME_BUILD_MARKERS,
        str(NVME_BUILD_PATH),
    )
    require_markers(
        read_text(root, VIRTIO_SCSI_SURVEY_BUILD_PATH),
        VIRTIO_SCSI_SURVEY_BUILD_MARKERS,
        str(VIRTIO_SCSI_SURVEY_BUILD_PATH),
    )
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, str(MAKEFILE_PATH))


def build_inventory_fixture() -> str:
    payload = {
        "build_test_names": EXPECTED_BUILD_TEST_NAMES,
        "shared_smoke_depend_steps": EXPECTED_SHARED_DEP_STEPS,
        "shared_test_depend_steps": EXPECTED_SHARED_DEP_STEPS,
        "throughput_anchor_depend_steps": ["throughput_parity_tests"],
    }
    return json.dumps(payload, indent=2) + "\n"


def build_fixture_text(markers: tuple[str, ...], counts: dict[str, int] | None = None) -> str:
    lines: list[str] = []
    if counts:
        for marker, expected in counts.items():
            lines.extend(marker for _ in range(expected))
    lines.extend(markers)
    return "\n".join(lines) + "\n"


def write_fixture(root: Path) -> None:
    files = {
        NOTE_PATH: build_fixture_text(NOTE_MARKERS),
        VIRTIO_NET_SURVEY_PATH: build_fixture_text(VIRTIO_NET_SURVEY_MARKERS),
        NVME_SURVEY_PATH: build_fixture_text(NVME_SURVEY_MARKERS),
        VIRTIO_SCSI_SURVEY_PATH: build_fixture_text(VIRTIO_SCSI_SURVEY_MARKERS),
        BUILD_PATH: build_fixture_text(BUILD_MARKERS, BUILD_COUNT_MARKERS),
        BUILD_INVENTORY_PATH: build_inventory_fixture(),
        NVME_BUILD_PATH: build_fixture_text(NVME_BUILD_MARKERS),
        VIRTIO_SCSI_SURVEY_BUILD_PATH: build_fixture_text(VIRTIO_SCSI_SURVEY_BUILD_MARKERS),
        MAKEFILE_PATH: build_fixture_text(MAKEFILE_MARKERS),
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-shared-route-split-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / BUILD_PATH).writeText if False else None
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if str(BUILD_PATH) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected shared-build marker failure")

        write_fixture(root)
        payload = json.loads((root / BUILD_INVENTORY_PATH).read_text(encoding="utf-8"))
        payload["build_test_names"].append("phase12-nvme-pci-direct-tests")
        (root / BUILD_INVENTORY_PATH).write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if str(BUILD_INVENTORY_PATH) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected inventory drift failure")

        write_fixture(root)
        (root / NVME_SURVEY_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if str(NVME_SURVEY_PATH) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected NVMe survey marker failure")

        write_fixture(root)
        (root / VIRTIO_SCSI_SURVEY_BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if str(VIRTIO_SCSI_SURVEY_BUILD_PATH) not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected virtio_scsi survey build marker failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-backed self-tests.",
    )
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
