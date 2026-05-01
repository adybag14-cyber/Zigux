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
CLOSURE_LEDGER = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"

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

REQUIRED_FILES = [CLOSURE_NOTE, CLOSURE_MANIFEST, CLOSURE_LEDGER] + EXPECTED_DOCS + EXPECTED_MANIFESTS + EXPECTED_DRIVERS + EXPECTED_TESTS

CLOSURE_NOTE_MARKERS = [
    "PHASE10_DOC_COUNT=9",
    "PHASE10_MANIFEST_COUNT=4",
    "PHASE10_DRIVER_COUNT=4",
    "PHASE10_TEST_COUNT=9",
    "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py",
    "PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig",
    "PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
    "PHASE10_LEDGER_RING_SURVEY_GATE=zigux/tests/phase10_virtio_ring_survey.zig",
    "PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig",
    "PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig",
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_3=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_6=make -C zigux phase10",
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

    closure_ledger = read_text(root, CLOSURE_LEDGER)
    for marker in LEDGER_MARKERS:
        if marker not in closure_ledger:
            missing.append(f"ledger:{marker}")

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
    closure_ledger = "\n".join(LEDGER_MARKERS) + "\n"
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
        elif rel_path == CLOSURE_LEDGER:
            path.write_text(closure_ledger, encoding="utf-8")
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

        (root / CLOSURE_LEDGER).unlink()
        expect_missing_file("missing_closure_ledger", root, CLOSURE_LEDGER)
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_core.zig").unlink()
        expect_missing_file("missing_core_lab_gate", root, "zigux/tests/phase10_virtio_core.zig")
        write_fixture(root)

        closure_note_path = root / CLOSURE_NOTE
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace(
                "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_CLOSURE_INVENTORY_GATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_inventory_gate_marker",
            root,
            "closure:PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
        )
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        manifest_path = root / CLOSURE_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docs"] = EXPECTED_DOCS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_docs_inventory", root, "manifest:docs")
        write_fixture(root)

        ledger_path = root / CLOSURE_LEDGER
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_LEDGER_INVENTORY_VALIDATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_inventory_validator_marker",
            root,
            "ledger:PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10-closure.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_exact_check_order",
            root,
            "ledger:PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = EXPECTED_TESTS[:-1] + ["zigux/tests/phase10_virtio_mmio_missing.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_tests_inventory", root, "manifest:tests")

    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST=pass")
    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST_CASE_COUNT=8")
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
    print("PHASE10_CLOSURE_INVENTORY_REQUIRED_GROUP_COUNT=5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
