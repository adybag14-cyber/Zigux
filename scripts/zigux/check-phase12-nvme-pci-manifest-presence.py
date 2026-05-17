#!/usr/bin/env python3
"""Fail-closed checker for Phase 12 NVMe PCI manifest presence drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REQUIRED_PRESENCE_FLAGS = {
    "preexisting_nvme_pci_zig_present": "drivers/nvme/host/pci.zig",
    "preexisting_nvme_pci_verifier_present": "drivers/nvme/host/pci_verify.zig",
    "preexisting_phase12_direct_test_present": "zigux/tests/phase12_nvme_pci.zig",
    "preexisting_phase12_build_present": "zigux/tests/phase12_build.zig",
    "preexisting_phase12_make_targets_present": "zigux/Makefile",
    "preexisting_phase12_fallback_note_present": "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "preexisting_phase12_reopen_governance_present": "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    "preexisting_phase12_slice_note_present": "Documentation/zigux/phase12-nvme-pci-slice.md",
    "preexisting_phase12_survey_note_present": "Documentation/zigux/phase12-nvme-pci-survey.md",
    "preexisting_phase12_survey_gate_present": "zigux/tests/phase12_nvme_pci_survey.zig",
}


def load_manifest(root: Path) -> dict:
    manifest_path = root / "zigux/tests/phase12_nvme_pci_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_manifest_presence(root: Path) -> tuple[list[str], int]:
    manifest = load_manifest(root)
    summary = manifest.get("survey_summary", {})
    failures: list[str] = []

    for field, rel_path in REQUIRED_PRESENCE_FLAGS.items():
        expected = summary.get(field)
        if not isinstance(expected, bool):
            failures.append(f"{field}: expected boolean field in survey_summary")
            continue

        actual = (root / rel_path).is_file()
        if actual != expected:
            failures.append(
                f"{field}: manifest says {expected!s} for {rel_path}, "
                f"but filesystem presence is {actual!s}"
            )

    return failures, len(REQUIRED_PRESENCE_FLAGS)


def run_live_check(root: Path) -> int:
    failures, checked = check_manifest_presence(root)
    if failures:
        print("PHASE12_NVME_PCI_MANIFEST_PRESENCE=fail")
        print(f"PHASE12_NVME_PCI_MANIFEST_PRESENCE_CHECKED={checked}")
        print(f"PHASE12_NVME_PCI_MANIFEST_PRESENCE_FAILURES={len(failures)}")
        for failure in failures:
            print(f"PHASE12_NVME_PCI_MANIFEST_PRESENCE_DETAIL={failure}")
        return 1

    print("PHASE12_NVME_PCI_MANIFEST_PRESENCE=pass")
    print(f"PHASE12_NVME_PCI_MANIFEST_PRESENCE_CHECKED={checked}")
    return 0


def write_manifest(root: Path, survey_summary: dict[str, bool | str]) -> None:
    manifest_dir = root / "zigux/tests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "lane_key": "P12-L08",
        "phase": "Phase 12",
        "survey_summary": survey_summary,
    }
    (manifest_dir / "phase12_nvme_pci_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def touch_required_files(root: Path) -> None:
    for rel_path in REQUIRED_PRESENCE_FLAGS.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12_nvme_pci_manifest_presence_") as tmp:
        root = Path(tmp)

        touch_required_files(root)
        write_manifest(root, {field: True for field in REQUIRED_PRESENCE_FLAGS})
        failures, _ = check_manifest_presence(root)
        assert not failures, failures
        cases += 1

        missing_path = root / "Documentation/zigux/phase12-nvme-pci-survey.md"
        missing_path.unlink()
        failures, _ = check_manifest_presence(root)
        assert any("preexisting_phase12_survey_note_present" in failure for failure in failures), failures
        cases += 1

        write_manifest(
            root,
            {
                "preexisting_nvme_pci_zig_present": True,
                "preexisting_nvme_pci_verifier_present": True,
                "preexisting_phase12_direct_test_present": True,
                "preexisting_phase12_build_present": True,
                "preexisting_phase12_make_targets_present": True,
                "preexisting_phase12_fallback_note_present": True,
                "preexisting_phase12_reopen_governance_present": "yes",
                "preexisting_phase12_slice_note_present": True,
                "preexisting_phase12_survey_note_present": True,
                "preexisting_phase12_survey_gate_present": True,
            },
        )
        failures, _ = check_manifest_presence(root)
        assert any("expected boolean field" in failure for failure in failures), failures
        cases += 1

    print("PHASE12_NVME_PCI_MANIFEST_PRESENCE_SELF_TEST=pass")
    print(f"PHASE12_NVME_PCI_MANIFEST_PRESENCE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Phase 12 NVMe PCI manifest presence flags against current-tree files."
    )
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_live_check(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
