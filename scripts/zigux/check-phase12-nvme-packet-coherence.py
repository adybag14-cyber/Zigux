#!/usr/bin/env python3
"""Fail-closed checker for the driver-local Phase 12 NVMe packet boundary."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

CHECK_NAME = "PHASE12_NVME_PACKET_COHERENCE"

MANIFEST_PATH = Path("zigux/tests/phase12_nvme_pci_manifest.json")
SHARED_BUILD_PATH = Path("zigux/tests/phase12_build.zig")
DIRECT_BUILD_PATH = Path("zigux/tests/phase12_nvme_pci_build.zig")
SURVEY_BUILD_PATH = Path("zigux/tests/phase12_nvme_pci_survey_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
GOVERNANCE_PATH = Path("Documentation/zigux/phase12-nvme-pci-reopen-governance.md")

REQUIRED_FILES = (
    MANIFEST_PATH,
    SHARED_BUILD_PATH,
    DIRECT_BUILD_PATH,
    SURVEY_BUILD_PATH,
    MAKEFILE_PATH,
    GOVERNANCE_PATH,
)

DIRECT_ROUTE_MARKERS = (
    "phase12-nvme-pci-direct-tests",
    "phase12-nvme-pci-verify-test",
    "phase12-nvme-pci-replay-wrapper-test",
    "phase12-nvme-pci-direct-test",
)

SURVEY_ROUTE_MARKERS = (
    "phase12-nvme-pci-survey-tests",
    "phase12-nvme-pci-survey-test",
)

MAKEFILE_MARKERS = (
    "phase12-nvme-pci-direct-test:",
    "$(ZIG) build phase12-nvme-pci-direct-test --build-file zigux/tests/phase12_nvme_pci_build.zig --summary all",
    "phase12-nvme-pci-survey-test:",
    "$(ZIG) build phase12-nvme-pci-survey-test --build-file zigux/tests/phase12_nvme_pci_survey_build.zig --summary all",
)

GOVERNANCE_MARKERS = (
    "stays outside the shared `phase12-smoke`, `phase12-test`, and aggregate `phase12` route",
    "`make -C zigux phase12-nvme-pci-direct-test`",
    "`make -C zigux phase12-nvme-pci-survey-test`",
)

FORBIDDEN_SHARED_BUILD_MARKERS = (
    "phase12_nvme_pci.zig",
    "phase12-nvme-pci-direct-test",
    "phase12-nvme-pci-survey-test",
    "drivers/nvme/host/pci.zig",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, rel_path: Path) -> str:
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {rel_path.as_posix()}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: Path) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label.as_posix()} missing marker: {marker}")


def require_absent_markers(text: str, markers: tuple[str, ...], label: Path) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label.as_posix()} unexpected marker: {marker}")


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object]:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    raise CheckFailure(f"{MANIFEST_PATH.as_posix()} missing gap entry: {gap_id}")


def check_manifest(root: Path) -> None:
    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckFailure(f"{MANIFEST_PATH.as_posix()} invalid JSON: {exc}") from exc

    queueing = manifest.get("roadmap_gap_check", {}).get("queueing_correctness", {})
    segmented = manifest.get("roadmap_gap_check", {}).get("segmented_rollout", {})
    throughput = manifest.get("roadmap_gap_check", {}).get("throughput_and_recovery_parity", {})

    if queueing.get("status") != "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_absent":
        raise CheckFailure("queueing_correctness status no longer matches the live shared-build boundary")
    if "does not yet wire the NVMe direct replay" not in str(queueing.get("current_surface", "")):
        raise CheckFailure("queueing_correctness current_surface must state that the shared Phase 12 build does not wire NVMe")
    if "shared Phase 12 build remains scoped to the virtio_net packet" not in str(queueing.get("blocked_by", "")):
        raise CheckFailure("queueing_correctness blocked_by must keep the shared-build scope explicit")

    if throughput.get("status") != "recovery_budget_summary_dedicated_direct_replay_present_throughput_gate_missing":
        raise CheckFailure("throughput_and_recovery_parity status drifted")
    if "dedicated direct replay" not in str(throughput.get("current_surface", "")):
        raise CheckFailure("throughput_and_recovery_parity current_surface must describe the dedicated direct replay route")

    if segmented.get("status") != "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_build_absent":
        raise CheckFailure("segmented_rollout status drifted")
    if "shared Phase 12 build still stays focused on the virtio_net packet" not in str(segmented.get("current_surface", "")):
        raise CheckFailure("segmented_rollout current_surface must keep the shared-build boundary explicit")

    direct_gap = find_gap(manifest, "phase12-nvme-direct-replay")
    if direct_gap.get("status") != "landed_on_master_shared_build_absent_dedicated_build_present":
        raise CheckFailure("phase12-nvme-direct-replay gap status drifted")
    if "dedicated direct replay remains the current review surface and is intentionally not wired through the shared Phase 12 build route" not in str(direct_gap.get("why_now", "")):
        raise CheckFailure("phase12-nvme-direct-replay why_now must keep the direct-only route explicit")

    shared_gap = find_gap(manifest, "phase12-nvme-shared-build-route")
    if shared_gap.get("status") != "shared_build_absent_direct_replay_and_survey_standalone":
        raise CheckFailure("phase12-nvme-shared-build-route gap status drifted")
    if "shared Phase 12 build route still stays scoped to the virtio_net packet" not in str(shared_gap.get("why_now", "")):
        raise CheckFailure("phase12-nvme-shared-build-route why_now must keep NVMe outside the shared route")


def check(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            raise CheckFailure(f"missing required file: {rel_path.as_posix()}")

    check_manifest(root)
    require_absent_markers(read_text(root, SHARED_BUILD_PATH), FORBIDDEN_SHARED_BUILD_MARKERS, SHARED_BUILD_PATH)
    require_markers(read_text(root, DIRECT_BUILD_PATH), DIRECT_ROUTE_MARKERS, DIRECT_BUILD_PATH)
    require_markers(read_text(root, SURVEY_BUILD_PATH), SURVEY_ROUTE_MARKERS, SURVEY_BUILD_PATH)
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, MAKEFILE_PATH)
    require_markers(read_text(root, GOVERNANCE_PATH), GOVERNANCE_MARKERS, GOVERNANCE_PATH)


def write_fixture(root: Path) -> None:
    fixture_manifest = {
        "roadmap_gap_check": {
            "queueing_correctness": {
                "status": "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_absent",
                "current_surface": "The bounded starter, verifier shard, dedicated survey gate, fallback map, slice note, survey note, and dedicated direct-build routes are all present on current master, while zigux/tests/phase12_build.zig still does not yet wire the NVMe direct replay.",
                "blocked_by": "The survey gate still carries the packet-local truthfulness checks, the verifier shard and helper-wrapper proofs still stay on the dedicated direct-build route, and the shared Phase 12 build remains scoped to the virtio_net packet while transport-backed queue execution remains outside the current packet.",
            },
            "throughput_and_recovery_parity": {
                "status": "recovery_budget_summary_dedicated_direct_replay_present_throughput_gate_missing",
                "current_surface": "The current starter records recovery reservation replay debt and budgeting through the dedicated direct replay and survey gate without a landed throughput benchmark or transport-backed reset replay.",
            },
            "segmented_rollout": {
                "status": "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_build_absent",
                "current_surface": "The fallback map, reopen-governance note, dedicated slice note, manifest anchor, survey note, survey gate, and dedicated direct-build route keep the current NVMe packet explicit as a bounded driver-local starter while the shared Phase 12 build still stays focused on the virtio_net packet.",
            },
        },
        "gaps": [
            {
                "id": "phase12-nvme-direct-replay",
                "status": "landed_on_master_shared_build_absent_dedicated_build_present",
                "why_now": "The dedicated direct replay remains the current review surface and is intentionally not wired through the shared Phase 12 build route.",
            },
            {
                "id": "phase12-nvme-shared-build-route",
                "status": "shared_build_absent_direct_replay_and_survey_standalone",
                "why_now": "The shared Phase 12 build route still stays scoped to the virtio_net packet while the dedicated survey gate and dedicated direct route remain driver-local.",
            },
        ],
    }

    files = {
        MANIFEST_PATH: json.dumps(fixture_manifest, indent=2) + "\n",
        SHARED_BUILD_PATH: "const std = @import(\"std\");\n// virtio-only shared route fixture\n",
        DIRECT_BUILD_PATH: "\n".join(DIRECT_ROUTE_MARKERS) + "\n",
        SURVEY_BUILD_PATH: "\n".join(SURVEY_ROUTE_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        GOVERNANCE_PATH: "\n".join(GOVERNANCE_MARKERS) + "\n",
    }
    for rel_path, text in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except CheckFailure as exc:
        if expected_fragment not in str(exc):
            raise
        return
    raise AssertionError(f"expected failure containing: {expected_fragment}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-nvme-packet-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / MANIFEST_PATH).write_text("{\n", encoding="utf-8")
        expect_failure(root, "invalid JSON")
        cases += 1

        write_fixture(root)
        text = (root / MANIFEST_PATH).read_text(encoding="utf-8").replace(
            "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_absent",
            "wrong-status",
            1,
        )
        (root / MANIFEST_PATH).write_text(text, encoding="utf-8")
        expect_failure(root, "queueing_correctness status")
        cases += 1

        write_fixture(root)
        (root / SHARED_BUILD_PATH).write_text("phase12-nvme-pci-direct-test\n", encoding="utf-8")
        expect_failure(root, SHARED_BUILD_PATH.as_posix())
        cases += 1

        write_fixture(root)
        (root / DIRECT_BUILD_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, DIRECT_BUILD_PATH.as_posix())
        cases += 1

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-nvme-pci-direct-test:\n", encoding="utf-8")
        expect_failure(root, MAKEFILE_PATH.as_posix())
        cases += 1

        write_fixture(root)
        (root / GOVERNANCE_PATH).write_text("broken\n", encoding="utf-8")
        expect_failure(root, GOVERNANCE_PATH.as_posix())
        cases += 1

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
