#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "drivers/net/virtio_net.zig",
    "drivers/scsi/virtio_scsi.zig",
    "drivers/nvme/host/pci_verify.zig",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_packet.zig",
    "zigux/tests/phase12_build.zig",
    "scripts/zigux/validate-phase12.py",
]

EXPECTED_ABSENT_FILES = [
    "drivers/nvme/host/pci.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_nvme_pci_survey.zig",
]

REQUIRED_MARKERS = {
    "zigux/tests/phase12_build.zig": [
        "../../drivers/net/virtio_net.zig",
        "\"phase12_virtio_net.zig\"",
        "\"phase12_virtio_net_syntax_lab.zig\"",
        "phase12-virtio-net-tests",
        "phase12-virtio-net-syntax-lab-tests",
        "run_virtio_net_contract_tests.setCwd(b.path(\"../..\"));",
        "run_virtio_net_syntax_tests.setCwd(b.path(\"../..\"));",
        "smoke_step.dependOn(&run_virtio_net_syntax_tests.step);",
        "test_step.dependOn(&run_virtio_net_contract_tests.step);",
        "test_step.dependOn(&run_virtio_net_syntax_tests.step);",
        "../../drivers/scsi/virtio_scsi.zig",
        "\"phase12_virtio_scsi.zig\"",
        "\"phase12_virtio_scsi_syntax_lab.zig\"",
        "\"phase12_virtio_scsi_repeated_replan_gate.zig\"",
        "\"phase12_virtio_scsi_packet.zig\"",
        "phase12-virtio-scsi-tests",
        "phase12-virtio-scsi-syntax-lab-tests",
        "phase12-virtio-scsi-repeated-replan-gate-tests",
        "phase12-virtio-scsi-packet-tests",
        "run_contract_tests.setCwd(b.path(\"../..\"));",
        "run_syntax_tests.setCwd(b.path(\"../..\"));",
        "run_repeated_replan_tests.setCwd(b.path(\"../..\"));",
        "run_packet_tests.setCwd(b.path(\"../..\"));",
        "smoke_step.dependOn(&run_repeated_replan_tests.step);",
        "smoke_step.dependOn(&run_packet_tests.step);",
        "test_step.dependOn(&run_repeated_replan_tests.step);",
        "test_step.dependOn(&run_packet_tests.step);",
        "b.step(\"smoke\", \"Run Phase 12 virtio syntax smoke\")",
        "b.step(\"test\", \"Run Phase 12 virtio packet tests\")",
    ],
    "scripts/zigux/validate-phase12.py": [
        "--self-test",
        "PHASE12_VALIDATION=pass",
        "PHASE12_VALIDATOR_SELF_TEST=pass",
        "UNEXPECTED_PHASE12_FILES_START",
        "drivers/nvme/host/pci.zig",
        "drivers/nvme/host/pci_verify.zig",
        "zigux/tests/phase12_nvme_pci.zig",
        "zigux/tests/phase12_nvme_pci_manifest.json",
        "zigux/tests/phase12_nvme_pci_survey.zig",
        "phase12_build.zig",
        "phase12_virtio_net.zig",
        "phase12_virtio_net_syntax_lab.zig",
        "phase12_virtio_net_survey.zig",
        "phase12_virtio_net_manifest.json",
        "phase12-virtio-net-survey.md",
        "phase12_virtio_scsi_syntax_lab.zig",
        "phase12_virtio_scsi_repeated_replan_gate.zig",
        "phase12_virtio_scsi_packet.zig",
    ],
}

FIXTURE_OVERRIDES = {
    "drivers/net/virtio_net.zig": "// fixture\n",
    "drivers/scsi/virtio_scsi.zig": "// fixture\n",
    "drivers/nvme/host/pci_verify.zig": "// fixture\n",
    "Documentation/zigux/phase12-virtio-net-survey.md": "# fixture\n",
    "zigux/tests/phase12_virtio_net.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_survey.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_manifest.json": "{}\n",
    "zigux/tests/phase12_virtio_scsi.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_packet.zig": "// fixture\n",
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def collect_unexpected_files(root: Path) -> list[str]:
    return [rel for rel in EXPECTED_ABSENT_FILES if (root / rel).exists()]


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return [], missing_markers, []

    return [], [], collect_unexpected_files(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()
    }
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_markers == [], case
    assert unexpected_files == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert unexpected_files == [], case
    assert missing_markers == [marker], case


def expect_unexpected_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert unexpected_files == [rel], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_phase12_virtio_net_driver", "drivers/net/virtio_net.zig"),
        ("missing_phase12_nvme_verify_shard", "drivers/nvme/host/pci_verify.zig"),
        (
            "missing_phase12_virtio_net_survey_note",
            "Documentation/zigux/phase12-virtio-net-survey.md",
        ),
        ("missing_phase12_virtio_net_contract_test", "zigux/tests/phase12_virtio_net.zig"),
        (
            "missing_phase12_virtio_net_syntax_lab",
            "zigux/tests/phase12_virtio_net_syntax_lab.zig",
        ),
        (
            "missing_phase12_virtio_net_survey_gate",
            "zigux/tests/phase12_virtio_net_survey.zig",
        ),
        (
            "missing_phase12_virtio_net_manifest",
            "zigux/tests/phase12_virtio_net_manifest.json",
        ),
        ("missing_phase12_driver", "drivers/scsi/virtio_scsi.zig"),
        ("missing_phase12_contract_test", "zigux/tests/phase12_virtio_scsi.zig"),
        (
            "missing_phase12_syntax_lab",
            "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
        ),
        (
            "missing_phase12_repeated_replan_gate",
            "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
        ),
        (
            "missing_phase12_packet_test",
            "zigux/tests/phase12_virtio_scsi_packet.zig",
        ),
        ("missing_phase12_build", "zigux/tests/phase12_build.zig"),
    ]

    unexpected_file_cases = [
        ("unexpected_nvme_driver", "drivers/nvme/host/pci.zig"),
        ("unexpected_nvme_contract_test", "zigux/tests/phase12_nvme_pci.zig"),
        ("unexpected_nvme_manifest", "zigux/tests/phase12_nvme_pci_manifest.json"),
        ("unexpected_nvme_survey_gate", "zigux/tests/phase12_nvme_pci_survey.zig"),
    ]

    marker_cases = [
        (
            "missing_phase12_build_virtio_net_driver_anchor",
            "zigux/tests/phase12_build.zig",
            "../../drivers/net/virtio_net.zig",
            "../../drivers/net/virtio_net_missing.zig",
            "zigux/tests/phase12_build.zig: ../../drivers/net/virtio_net.zig",
        ),
        (
            "missing_phase12_build_virtio_net_contract_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_net.zig\"",
            "\"phase12_virtio_net_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_net.zig\"",
        ),
        (
            "missing_phase12_build_virtio_net_syntax_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_net_syntax_lab.zig\"",
            "\"phase12_virtio_net_syntax_lab_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_net_syntax_lab.zig\"",
        ),
        (
            "missing_phase12_build_virtio_net_smoke_dependency",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_virtio_net_syntax_tests.step);",
            "smoke_step.dependOn(&run_virtio_net_syntax_gate.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_virtio_net_syntax_tests.step);",
        ),
        (
            "missing_phase12_build_virtio_net_test_dependency",
            "zigux/tests/phase12_build.zig",
            "test_step.dependOn(&run_virtio_net_contract_tests.step);",
            "test_step.dependOn(&run_virtio_net_contract_gate.step);",
            "zigux/tests/phase12_build.zig: test_step.dependOn(&run_virtio_net_contract_tests.step);",
        ),
        (
            "missing_phase12_build_driver_anchor",
            "zigux/tests/phase12_build.zig",
            "../../drivers/scsi/virtio_scsi.zig",
            "../../drivers/scsi/virtio_scsi_missing.zig",
            "zigux/tests/phase12_build.zig: ../../drivers/scsi/virtio_scsi.zig",
        ),
        (
            "missing_phase12_build_contract_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_scsi.zig\"",
            "\"phase12_virtio_scsi_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_scsi.zig\"",
        ),
        (
            "missing_phase12_build_syntax_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_scsi_syntax_lab.zig\"",
            "\"phase12_virtio_scsi_syntax_lab_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_scsi_syntax_lab.zig\"",
        ),
        (
            "missing_phase12_build_repeated_replan_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_scsi_repeated_replan_gate.zig\"",
            "\"phase12_virtio_scsi_repeated_replan_gate_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_scsi_repeated_replan_gate.zig\"",
        ),
        (
            "missing_phase12_build_packet_source",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_scsi_packet.zig\"",
            "\"phase12_virtio_scsi_packet_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_scsi_packet.zig\"",
        ),
        (
            "missing_phase12_build_smoke_dependency",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_repeated_replan_tests.step);",
            "smoke_step.dependOn(&run_repeated_replan_gate.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_repeated_replan_tests.step);",
        ),
        (
            "missing_phase12_build_packet_smoke_dependency",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_packet_tests.step);",
            "smoke_step.dependOn(&run_packet_gate.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_packet_tests.step);",
        ),
        (
            "missing_phase12_build_test_dependency",
            "zigux/tests/phase12_build.zig",
            "test_step.dependOn(&run_repeated_replan_tests.step);",
            "test_step.dependOn(&run_repeated_replan_gate.step);",
            "zigux/tests/phase12_build.zig: test_step.dependOn(&run_repeated_replan_tests.step);",
        ),
        (
            "missing_phase12_build_packet_test_dependency",
            "zigux/tests/phase12_build.zig",
            "test_step.dependOn(&run_packet_tests.step);",
            "test_step.dependOn(&run_packet_gate.step);",
            "zigux/tests/phase12_build.zig: test_step.dependOn(&run_packet_tests.step);",
        ),
        (
            "missing_validator_nvme_absence_section",
            "scripts/zigux/validate-phase12.py",
            "UNEXPECTED_PHASE12_FILES_START",
            "UNEXPECTED_FILES_START",
            "scripts/zigux/validate-phase12.py: UNEXPECTED_PHASE12_FILES_START",
        ),
        (
            "missing_validator_nvme_driver_marker",
            "scripts/zigux/validate-phase12.py",
            "drivers/nvme/host/pci.zig",
            "drivers/nvme/host/pci_missing.zig",
            "scripts/zigux/validate-phase12.py: drivers/nvme/host/pci.zig",
        ),
        (
            "missing_validator_nvme_verify_marker",
            "scripts/zigux/validate-phase12.py",
            "drivers/nvme/host/pci_verify.zig",
            "drivers/nvme/host/pci_verify_missing.zig",
            "scripts/zigux/validate-phase12.py: drivers/nvme/host/pci_verify.zig",
        ),
        (
            "missing_validator_virtio_net_manifest_marker",
            "scripts/zigux/validate-phase12.py",
            "phase12_virtio_net_manifest.json",
            "phase12_virtio_net_manifest_missing.json",
            "scripts/zigux/validate-phase12.py: phase12_virtio_net_manifest.json",
        ),
        (
            "missing_validator_packet_marker",
            "scripts/zigux/validate-phase12.py",
            "phase12_virtio_scsi_packet.zig",
            "phase12_virtio_scsi_packet_missing.zig",
            "scripts/zigux/validate-phase12.py: phase12_virtio_scsi_packet.zig",
        ),
        (
            "missing_validator_self_test_flag",
            "scripts/zigux/validate-phase12.py",
            "--self-test",
            "--selftest",
            "scripts/zigux/validate-phase12.py: --self-test",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel in unexpected_file_cases:
            path = tmp_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// unexpected fixture\n", encoding="utf-8")
            expect_unexpected_file(case, tmp_root, rel)
            path.unlink()

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(unexpected_file_cases) + len(marker_cases)
    print("PHASE12_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shipped packet, require the parked "
            "NVMe verifier shard, and fail closed if direct NVMe replay files "
            "appear without validator maintenance."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run validator self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, unexpected_files = validate(ROOT)
    if missing_files:
        print("PHASE12_VALIDATION=fail")
        print("MISSING_PHASE12_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE12_FILES_END")
        return 1

    if missing_markers:
        print("PHASE12_VALIDATION=fail")
        print("MISSING_PHASE12_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE12_MARKERS_END")
        return 1

    if unexpected_files:
        print("PHASE12_VALIDATION=fail")
        print("UNEXPECTED_PHASE12_FILES_START")
        for item in unexpected_files:
            print(item)
        print("UNEXPECTED_PHASE12_FILES_END")
        return 1

    print("PHASE12_VALIDATION=pass")
    print(f"PHASE12_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE12_EXPECTED_ABSENT_FILE_COUNT={len(EXPECTED_ABSENT_FILES)}")
    print(
        "PHASE12_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())