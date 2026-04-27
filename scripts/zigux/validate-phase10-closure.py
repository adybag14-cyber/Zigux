#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]


required_files = [
    ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-core-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-module-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-mmio-survey.md",
    ROOT / "scripts" / "zigux" / "validate-phase10-closure.py",
    ROOT / "zigux" / "Makefile",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md",
    ROOT / "drivers" / "virtio" / "virtio.zig",
    ROOT / "drivers" / "virtio" / "virtio_ring.zig",
    ROOT / "drivers" / "virtio" / "virtio_input.zig",
    ROOT / "zigux" / "tests" / "phase10_build.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_core.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_closure_manifest.json",
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE10_CLOSURE_FILES_END")
    sys.exit(1)

closure = (ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md").read_text(encoding="utf-8")
makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
manifest = load_json(ROOT / "zigux" / "tests" / "phase10_closure_manifest.json")

required_closure_markers = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_CLOSURE_EVIDENCE=verified",
    "PHASE10_DOC_COUNT=7",
    "PHASE10_MANIFEST_COUNT=3",
    "PHASE10_DRIVER_COUNT=3",
    "PHASE10_TEST_COUNT=6",
    "PHASE10_HAS_VIRTIO_MMIO_ZIG=no",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
]
required_makefile_markers = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]
required_workflow_markers = [
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]
missing_markers: list[str] = []
for marker in required_closure_markers:
    if marker not in closure:
        missing_markers.append(f"closure:{marker}")
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f"make:{marker}")
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f"workflow:{marker}")

if manifest.get("phase") != "Phase 10":
    missing_markers.append("manifest:phase=Phase 10")
if manifest.get("status") != "active":
    missing_markers.append("manifest:status=active")
if manifest.get("tranche") != "virtio-lab-bundle":
    missing_markers.append("manifest:tranche=virtio-lab-bundle")
if manifest.get("doc_count") != 7:
    missing_markers.append(f'manifest:doc_count={manifest.get("doc_count")}')
if manifest.get("manifest_count") != 3:
    missing_markers.append(f'manifest:manifest_count={manifest.get("manifest_count")}')
if manifest.get("driver_count") != 3:
    missing_markers.append(f'manifest:driver_count={manifest.get("driver_count")}')
if manifest.get("test_count") != 6:
    missing_markers.append(f'manifest:test_count={manifest.get("test_count")}')
if manifest.get("has_virtio_mmio_zig") is not False:
    missing_markers.append(f'manifest:has_virtio_mmio_zig={manifest.get("has_virtio_mmio_zig")}')

for field in ("docs", "manifests", "drivers", "tests", "exact_checks"):
    value = manifest.get(field)
    if not isinstance(value, list) or not value:
        missing_markers.append(f"manifest:{field}:expected_non_empty_list")
        continue
    for rel in value:
        if not isinstance(rel, str):
            missing_markers.append(f"manifest:{field}:non_string_entry")
            continue
        if field != "exact_checks" and not (ROOT / rel).exists():
            missing_markers.append(f"manifest_file:{rel}")

expected_exact_checks = {
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
}
if set(manifest.get("exact_checks", [])) != expected_exact_checks:
    missing_markers.append("manifest:exact_checks:mismatch")

if missing_markers:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE10_CLOSURE_MARKERS_END")
    sys.exit(1)

print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
    f"{len(required_closure_markers) + len(required_makefile_markers) + len(required_workflow_markers)}"
)
