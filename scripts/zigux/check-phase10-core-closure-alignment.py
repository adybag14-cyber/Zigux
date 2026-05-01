#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
]

CLOSURE_MARKERS = [
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "zigux/tests/phase10_virtio_core_survey.zig",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_CORE_SLICE=Documentation/zigux/phase10-virtio-core-slice.md",
    "PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig",
    "PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
    "PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json",
]

CORE_SLICE_MARKERS = [
    "PHASE10_SLICE=virtio-core-lab-starter",
    "drivers/virtio/virtio.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_build.zig",
    "bounded config-generation observation surface",
    "bounded remove-side handoff",
]

CORE_MANIFEST_GAP_IDS = {
    "phase10-closure-evidence-gate",
    "phase10-virtio-core-lab-gate",
    "phase10-virtio-core-slice-note",
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-core-probe-remove-lifecycle",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    check_markers(
        missing,
        "closure",
        read_text(root, "Documentation/zigux/phase10-closure-evidence.md"),
        CLOSURE_MARKERS,
    )
    check_markers(
        missing,
        "ledger",
        read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"),
        LEDGER_MARKERS,
    )
    check_markers(
        missing,
        "core_slice",
        read_text(root, "Documentation/zigux/phase10-virtio-core-slice.md"),
        CORE_SLICE_MARKERS,
    )

    manifest = load_json(root, "zigux/tests/phase10_virtio_core_manifest.json")
    if not isinstance(manifest, dict):
        return [], ["core_manifest:type"]

    expected_scalars = {
        "lane_key": "P10-L03",
        "phase": "Phase 10",
        "anchor": "drivers/virtio/virtio.c",
    }
    for key, value in expected_scalars.items():
        if manifest.get(key) != value:
            missing.append(f"core_manifest:{key}={manifest.get(key)!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("core_manifest:survey_summary")
    else:
        if summary.get("preexisting_phase10_core_slice_note_present") is not True:
            missing.append("core_manifest:survey_summary:preexisting_phase10_core_slice_note_present")
        if summary.get("preexisting_phase10_closure_note_present") is not True:
            missing.append("core_manifest:survey_summary:preexisting_phase10_closure_note_present")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("core_manifest:gaps")
    else:
        gap_ids = {
            item.get("id")
            for item in gaps
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        for gap_id in sorted(CORE_MANIFEST_GAP_IDS):
            if gap_id not in gap_ids:
                missing.append(f"core_manifest:gap:{gap_id}")

    return [], missing


def write_fixture(root: Path) -> None:
    files = {
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-core-slice.md": "\n".join(CORE_SLICE_MARKERS) + "\n",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_core_manifest.json": json.dumps(
            {
                "lane_key": "P10-L03",
                "phase": "Phase 10",
                "anchor": "drivers/virtio/virtio.c",
                "survey_summary": {
                    "preexisting_phase10_core_slice_note_present": True,
                    "preexisting_phase10_closure_note_present": True,
                },
                "gaps": [{"id": gap_id} for gap_id in sorted(CORE_MANIFEST_GAP_IDS)],
            },
            indent=2,
        )
        + "\n",
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-core-closure-self-test:{label}:missing_files:{','.join(missing_files)}")
    if marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-core-closure-self-test:{label}:expected:{marker}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_closure_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-core-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        closure_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            original_closure.replace("zigux/tests/phase10_virtio_core_manifest.json", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_core_manifest_marker",
            root,
            "closure:zigux/tests/phase10_virtio_core_manifest.json",
        )
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_core_manifest_marker",
            root,
            "ledger:PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json",
        )
        write_fixture(root)

        slice_path = root / "Documentation/zigux/phase10-virtio-core-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("bounded config-generation observation surface", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "core_slice_marker",
            root,
            "core_slice:bounded config-generation observation surface",
        )
        write_fixture(root)

        manifest_path = root / "zigux/tests/phase10_virtio_core_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_phase10_core_slice_note_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "core_manifest_summary_flag",
            root,
            "core_manifest:survey_summary:preexisting_phase10_core_slice_note_present",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"] = [item for item in manifest["gaps"] if item["id"] != "phase10-config-delivery-disposition-helper"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "core_manifest_gap_id",
            root,
            "core_manifest:gap:phase10-config-delivery-disposition-helper",
        )

    print("PHASE10_CORE_CLOSURE_ALIGNMENT_SELF_TEST=pass")
    print("PHASE10_CORE_CLOSURE_ALIGNMENT_SELF_TEST_CASE_COUNT=5")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_CORE_CLOSURE_ALIGNMENT=fail")
    print("MISSING_PHASE10_CORE_CLOSURE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_CORE_CLOSURE_FILES_END")
    sys.exit(1)

if missing_markers:
    print("PHASE10_CORE_CLOSURE_ALIGNMENT=fail")
    print("MISSING_PHASE10_CORE_CLOSURE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_CORE_CLOSURE_MARKERS_END")
    sys.exit(1)

print("PHASE10_CORE_CLOSURE_ALIGNMENT=pass")
print(f"PHASE10_CORE_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE10_CORE_CLOSURE_REQUIRED_MARKER_COUNT="
    f"{len(CLOSURE_MARKERS) + len(LEDGER_MARKERS) + len(CORE_SLICE_MARKERS) + len(CORE_MANIFEST_GAP_IDS) + 5}"
)
