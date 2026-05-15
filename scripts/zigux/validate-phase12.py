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
    "drivers/nvme/host/pci.zig",
    "drivers/nvme/host/pci_verify.zig",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    "zigux/tests/phase12_virtio_scsi_packet.zig",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "scripts/zigux/check-build-only-phase12-surface.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "scripts/zigux/validate-phase12.py",
]

EXPECTED_ABSENT_FILES: list[str] = []

REQUIRED_MARKERS = {
    "Documentation/zigux/phase12-release-readiness-survey.md": [
        "`PHASE12_STATUS=active`",
        "`PHASE12_RELEASE_CLOSED=no`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "make -C zigux phase12-validate",
    ],
    "Documentation/zigux/phase12-nvme-pci-survey.md": [
        "`PHASE12_STATUS=starter-present-slice-note-survey-packet`",
        "`PHASE12_LANE=P12-L08`",
        "current `master` now carries `drivers/nvme/host/pci.zig`",
        "planPrpBufferShape()",
        "recoveryQueueRestoreSummary()",
        "summarizeDroppedIoRetirement()",
        "still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig`",
    ],
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
        "../../drivers/scsi/virtio_scsi.zig",
        "\"phase12_virtio_scsi.zig\"",
        "\"phase12_virtio_scsi_syntax_lab.zig\"",
        "\"phase12_virtio_scsi_repeated_replan_gate.zig\"",
        "\"phase12_virtio_scsi_repeated_rollback_gate.zig\"",
        "\"phase12_virtio_scsi_packet.zig\"",
        "phase12-virtio-scsi-tests",
        "phase12-virtio-scsi-syntax-lab-tests",
        "phase12-virtio-scsi-repeated-replan-gate-tests",
        "phase12-virtio-scsi-repeated-rollback-gate-tests",
        "phase12-virtio-scsi-packet-tests",
        "run_contract_tests.setCwd(b.path(\"../..\"));",
        "run_syntax_tests.setCwd(b.path(\"../..\"));",
        "run_repeated_replan_tests.setCwd(b.path(\"../..\"));",
        "run_repeated_rollback_tests.setCwd(b.path(\"../..\"));",
        "run_packet_tests.setCwd(b.path(\"../..\"));",
        "b.step(\"smoke\", \"Run Phase 12 virtio syntax smoke\")",
        "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        "b.step(\"test\", \"Run Phase 12 virtio packet tests\")",
        "test_step.dependOn(&run_repeated_rollback_tests.step);",
    ],
    "zigux/tests/phase12_nvme_pci_manifest.json": [
        "\"lane_key\": \"P12-L08\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/nvme/host/pci.c\"",
        "\"preexisting_nvme_pci_zig_present\": true",
        "\"preexisting_nvme_pci_verifier_present\": true",
        "\"preexisting_phase12_direct_test_present\": true",
        "\"preexisting_phase12_survey_note_present\": true",
        "\"preexisting_phase12_survey_gate_present\": true",
    ],
    "zigux/tests/phase12_nvme_pci_survey.zig": [
        "phase12 nvme pci survey manifest keeps the bounded queue-and-recovery packet truthful",
        "phase12 nvme pci survey note stays aligned with the bounded queue-and-recovery starter",
        "phase12 nvme pci survey gate keeps present lane files explicit",
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        "drivers/nvme/host/pci_verify.zig",
        "zigux/tests/phase12_nvme_pci.zig",
    ],
    "scripts/zigux/validate-phase12.py": [
        "--self-test",
        "PHASE12_VALIDATION=pass",
        "PHASE12_VALIDATOR_SELF_TEST=pass",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
        "Documentation/zigux/phase12-nvme-pci-slice.md",
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        "zigux/tests/phase12_nvme_pci.zig",
        "zigux/tests/phase12_nvme_pci_manifest.json",
        "zigux/tests/phase12_nvme_pci_survey.zig",
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
    ],
}

FIXTURE_OVERRIDES = {
    "drivers/net/virtio_net.zig": "// fixture\n",
    "drivers/scsi/virtio_scsi.zig": "// fixture\n",
    "drivers/nvme/host/pci.zig": "// fixture\n",
    "drivers/nvme/host/pci_verify.zig": "// fixture\n",
    "Documentation/zigux/phase12-release-closure-checklist.md": "# fixture\n",
    "Documentation/zigux/phase12-virtio-net-survey.md": "# fixture\n",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md": "# fixture\n",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md": "# fixture\n",
    "Documentation/zigux/phase12-nvme-pci-slice.md": "# fixture\n",
    "zigux/tests/phase12_virtio_net.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_survey.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_manifest.json": "{}\n",
    "zigux/tests/phase12_virtio_scsi.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_packet.zig": "// fixture\n",
    "zigux/tests/phase12_nvme_pci.zig": "// fixture\n",
    "zigux/tests/phase12_nvme_pci_manifest.json": "{\n  \"lane_key\": \"P12-L08\",\n  \"phase\": \"Phase 12\",\n  \"anchor\": \"drivers/nvme/host/pci.c\",\n  \"survey_summary\": {\n    \"preexisting_nvme_pci_zig_present\": true,\n    \"preexisting_nvme_pci_verifier_present\": true,\n    \"preexisting_phase12_direct_test_present\": true,\n    \"preexisting_phase12_survey_note_present\": true,\n    \"preexisting_phase12_survey_gate_present\": true\n  }\n}\n",
    "zigux/tests/phase12_nvme_pci_survey.zig": "// phase12 nvme pci survey manifest keeps the bounded queue-and-recovery packet truthful\n// phase12 nvme pci survey note stays aligned with the bounded queue-and-recovery starter\n// phase12 nvme pci survey gate keeps present lane files explicit\n// Documentation/zigux/phase12-nvme-pci-survey.md\n// drivers/nvme/host/pci_verify.zig\n// zigux/tests/phase12_nvme_pci.zig\n",
    "scripts/zigux/check-build-only-phase12-surface.py": "#!/usr/bin/env python3\n",
    "scripts/zigux/check-phase12-release-readiness-packet.py": "#!/usr/bin/env python3\n",
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
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
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


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_phase12_nvme_driver", "drivers/nvme/host/pci.zig"),
        ("missing_phase12_nvme_verify_shard", "drivers/nvme/host/pci_verify.zig"),
        ("missing_phase12_release_closure_checklist", "Documentation/zigux/phase12-release-closure-checklist.md"),
        ("missing_phase12_nvme_survey_note", "Documentation/zigux/phase12-nvme-pci-survey.md"),
        ("missing_phase12_nvme_fallback_note", "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"),
        ("missing_phase12_nvme_reopen_governance", "Documentation/zigux/phase12-nvme-pci-reopen-governance.md"),
        ("missing_phase12_nvme_slice_note", "Documentation/zigux/phase12-nvme-pci-slice.md"),
        ("missing_phase12_direct_repeated_rollback_gate", "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"),
        ("missing_phase12_nvme_direct_test", "zigux/tests/phase12_nvme_pci.zig"),
        ("missing_phase12_nvme_manifest", "zigux/tests/phase12_nvme_pci_manifest.json"),
        ("missing_phase12_nvme_survey_gate", "zigux/tests/phase12_nvme_pci_survey.zig"),
        ("missing_phase12_build_only_surface_checker", "scripts/zigux/check-build-only-phase12-surface.py"),
        ("missing_phase12_release_readiness_checker", "scripts/zigux/check-phase12-release-readiness-packet.py"),
    ]

    marker_cases = [
        (
            "missing_release_readiness_status_marker",
            "Documentation/zigux/phase12-release-readiness-survey.md",
            "`PHASE12_STATUS=active`",
            "`PHASE12_STATUS=inactive`",
            "Documentation/zigux/phase12-release-readiness-survey.md: `PHASE12_STATUS=active`",
        ),
        (
            "missing_release_readiness_closure_checklist_marker",
            "Documentation/zigux/phase12-release-readiness-survey.md",
            "`Documentation/zigux/phase12-release-closure-checklist.md`",
            "`Documentation/zigux/phase12-release-closure-checklist-missing.md`",
            "Documentation/zigux/phase12-release-readiness-survey.md: `Documentation/zigux/phase12-release-closure-checklist.md`",
        ),
        (
            "missing_phase12_build_repeated_rollback_source_marker",
            "zigux/tests/phase12_build.zig",
            "\"phase12_virtio_scsi_repeated_rollback_gate.zig\"",
            "\"phase12_virtio_scsi_repeated_rollback_gate_missing.zig\"",
            "zigux/tests/phase12_build.zig: \"phase12_virtio_scsi_repeated_rollback_gate.zig\"",
        ),
        (
            "missing_phase12_build_repeated_rollback_step_marker",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
            "smoke_step.dependOn(&run_repeated_replan_tests.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        ),
        (
            "missing_nvme_survey_lane_marker",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "`PHASE12_LANE=P12-L08`",
            "`PHASE12_LANE=P12-L07`",
            "Documentation/zigux/phase12-nvme-pci-survey.md: `PHASE12_LANE=P12-L08`",
        ),
        (
            "missing_nvme_survey_recovery_marker",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "recoveryQueueRestoreSummary()",
            "recoveryRestoreSummary()",
            "Documentation/zigux/phase12-nvme-pci-survey.md: recoveryQueueRestoreSummary()",
        ),
        (
            "missing_nvme_manifest_lane_key_marker",
            "zigux/tests/phase12_nvme_pci_manifest.json",
            "\"lane_key\": \"P12-L08\"",
            "\"lane_key\": \"P12-L05\"",
            "zigux/tests/phase12_nvme_pci_manifest.json: \"lane_key\": \"P12-L08\"",
        ),
        (
            "missing_nvme_manifest_survey_gate_marker",
            "zigux/tests/phase12_nvme_pci_manifest.json",
            "\"preexisting_phase12_survey_gate_present\": true",
            "\"preexisting_phase12_survey_gate_present\": false",
            "zigux/tests/phase12_nvme_pci_manifest.json: \"preexisting_phase12_survey_gate_present\": true",
        ),
        (
            "missing_nvme_survey_gate_marker",
            "zigux/tests/phase12_nvme_pci_survey.zig",
            "phase12 nvme pci survey gate keeps present lane files explicit",
            "phase12 nvme pci survey gate keeps lane files explicit",
            "zigux/tests/phase12_nvme_pci_survey.zig: phase12 nvme pci survey gate keeps present lane files explicit",
        ),
        (
            "missing_validator_self_test_flag",
            "scripts/zigux/validate-phase12.py",
            "--self-test",
            "--selftest",
            "scripts/zigux/validate-phase12.py: --self-test",
        ),
        (
            "missing_validator_release_closure_checklist_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-release-closure-checklist.md",
            "Documentation/zigux/phase12-release-closure-checklist-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-release-closure-checklist.md",
        ),
        (
            "missing_validator_nvme_survey_note_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "Documentation/zigux/phase12-nvme-pci-survey-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-nvme-pci-survey.md",
        ),
        (
            "missing_validator_release_readiness_checker_marker",
            "scripts/zigux/validate-phase12.py",
            "scripts/zigux/check-phase12-release-readiness-packet.py",
            "scripts/zigux/check-phase12-release-readiness-missing.py",
            "scripts/zigux/validate-phase12.py: scripts/zigux/check-phase12-release-readiness-packet.py",
        ),
        (
            "missing_validator_expected_absent_count_marker",
            "scripts/zigux/validate-phase12.py",
            "PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
            "PHASE12_EXPECTED_ABSENT_FILE_COUNT=1",
            "scripts/zigux/validate-phase12.py: PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
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

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE12_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shipped packet, the shared release-readiness "
            "fallback note, the release-closure companion, the dedicated support checker, "
            "and the bounded NVMe starter, verifier shard, direct replay, survey packet, "
            "and manifest surfaces."
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