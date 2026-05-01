#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CLOSURE_NOTE = "Documentation/zigux/phase10-closure-evidence.md"
CLOSURE_MANIFEST = "zigux/tests/phase10_closure_manifest.json"

EXPECTED_DOCS = [
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_MANIFESTS = [
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

EXPECTED_DRIVERS = [
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_mmio.zig",
]

EXPECTED_TESTS = [
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

REQUIRED_FILES = [CLOSURE_NOTE, CLOSURE_MANIFEST] + EXPECTED_DOCS + EXPECTED_MANIFESTS + EXPECTED_DRIVERS + EXPECTED_TESTS

CLOSURE_NOTE_MARKERS = [
    "PHASE10_DOC_COUNT=9",
    "PHASE10_MANIFEST_COUNT=4",
    "PHASE10_DRIVER_COUNT=4",
    "PHASE10_TEST_COUNT=9",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    closure_note = read_text(root, CLOSURE_NOTE)
    for marker in CLOSURE_NOTE_MARKERS:
        if marker not in closure_note:
            missing.append(f"closure:{marker}")

    manifest = load_json(root, CLOSURE_MANIFEST)
    if not isinstance(manifest, dict):
        missing.append("manifest:type")
        return [], missing

    expected_arrays = {
        "docs": EXPECTED_DOCS,
        "manifests": EXPECTED_MANIFESTS,
        "drivers": EXPECTED_DRIVERS,
        "tests": EXPECTED_TESTS,
    }
    for key, expected in expected_arrays.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}")

    expected_counts = {
        "doc_count": len(EXPECTED_DOCS),
        "manifest_count": len(EXPECTED_MANIFESTS),
        "driver_count": len(EXPECTED_DRIVERS),
        "test_count": len(EXPECTED_TESTS),
    }
    for key, expected in expected_counts.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}")

    return [], missing


def write_fixture(root: Path) -> None:
    closure_note = "\n".join(CLOSURE_NOTE_MARKERS) + "\n"
    closure_manifest = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": len(EXPECTED_DOCS),
        "manifest_count": len(EXPECTED_MANIFESTS),
        "driver_count": len(EXPECTED_DRIVERS),
        "test_count": len(EXPECTED_TESTS),
        "docs": EXPECTED_DOCS,
        "manifests": EXPECTED_MANIFESTS,
        "drivers": EXPECTED_DRIVERS,
        "tests": EXPECTED_TESTS,
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == CLOSURE_NOTE:
            path.write_text(closure_note, encoding="utf-8")
        elif rel_path == CLOSURE_MANIFEST:
            path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        elif rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:unexpected_markers:{','.join(missing_markers)}"
        )
    if rel_path not in missing_files:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:expected_missing_file:{rel_path}:actual:{','.join(missing_files) if missing_files else 'none'}"
        )


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:unexpected_files:{','.join(missing_files)}"
        )
    if marker not in missing_markers:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:expected_marker:{marker}:actual:{','.join(missing_markers) if missing_markers else 'none'}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-inventory-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        (root / "Documentation/zigux/phase10-virtio-input-module-slice.md").unlink()
        expect_missing_file(
            "missing_slice_doc",
            root,
            "Documentation/zigux/phase10-virtio-input-module-slice.md",
        )
        write_fixture(root)

        manifest_path = root / CLOSURE_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docs"] = EXPECTED_DOCS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_docs_inventory", root, "manifest:docs")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = EXPECTED_TESTS[:-1] + ["zigux/tests/phase10_virtio_mmio_missing.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_tests_inventory", root, "manifest:tests")

    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST=pass")
    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_CLOSURE_INVENTORY=fail")
        print("MISSING_PHASE10_CLOSURE_INVENTORY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_INVENTORY_FILES_END")
        return 1
    if missing_markers:
        print("PHASE10_CLOSURE_INVENTORY=fail")
        print("MISSING_PHASE10_CLOSURE_INVENTORY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CLOSURE_INVENTORY_MARKERS_END")
        return 1

    print("PHASE10_CLOSURE_INVENTORY=pass")
    print(f"PHASE10_CLOSURE_INVENTORY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE10_CLOSURE_INVENTORY_REQUIRED_GROUP_COUNT=4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
