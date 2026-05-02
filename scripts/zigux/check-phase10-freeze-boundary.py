#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent

REQUIRED_FILES = [
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_LANE_KEYS = {
    "core": "P10-L03",
    "ring": "P10-L08",
    "input": "P10-L13",
    "mmio": "P10-L18",
}

EXPECTED_SCOREBOARD_EVIDENCE = {
    "virtqueue_wrappers": [
        "drivers/virtio/virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "Documentation/zigux/phase10-virtio-ring-survey.md",
    ],
    "mmio_wrappers": [
        "drivers/virtio/virtio_mmio.zig",
        "zigux/tests/phase10_virtio_mmio.zig",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "Documentation/zigux/phase10-virtio-mmio-slice.md",
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    ],
    "lab_only_driver_validation": [
        "zigux/tests/phase10_build.zig",
        "scripts/zigux/check-phase10-closure-inventory.py",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/validate-phase10-closure.py",
        "Documentation/zigux/phase10-closure-evidence.md",
        "zigux/Makefile",
        ".github/workflows/zigux-bootstrap.yml",
    ],
    "dual_implementations_for_risky_areas": [
        "Documentation/zigux/phase10-closure-evidence.md",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "zigux/tests/phase10_virtio_input_manifest.json",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
    ],
}

SURVEY_MANIFEST_PATHS = {
    "core": "zigux/tests/phase10_virtio_core_manifest.json",
    "ring": "zigux/tests/phase10_virtio_ring_manifest.json",
    "input": "zigux/tests/phase10_virtio_input_manifest.json",
    "mmio": "zigux/tests/phase10_virtio_mmio_manifest.json",
}

LEDGER_MARKERS = [
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L03",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L08",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=drivers/virtio/virtio_ring.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md",
    "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-slice.md,Documentation/zigux/phase10-virtio-mmio-survey.md",
    "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=zigux/tests/phase10_build.zig,scripts/zigux/check-phase10-closure-inventory.py,scripts/zigux/validate-phase10.py,scripts/zigux/validate-phase10-closure.py,Documentation/zigux/phase10-closure-evidence.md,zigux/Makefile,.github/workflows/zigux-bootstrap.yml",
    "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md,zigux/tests/phase10_virtio_ring_manifest.json,zigux/tests/phase10_virtio_input_manifest.json,zigux/tests/phase10_virtio_mmio_manifest.json",
]

MMIO_SURVEY_MARKERS = [
    "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
    "PHASE10_FREEZE_BOUNDARY_STATUS=aligned",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
    "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
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

    closure_manifest = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if not isinstance(closure_manifest, dict):
        missing.append("closure_manifest:type")
        return [], missing

    survey_provenance = closure_manifest.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing.append("closure_manifest:survey_provenance")
    else:
        if survey_provenance.get("source") != "manifest_derived":
            missing.append("closure_manifest:survey_provenance:source")
        if survey_provenance.get("lane_keys") != EXPECTED_LANE_KEYS:
            missing.append("closure_manifest:survey_provenance:lane_keys")

        surveyed_commits = survey_provenance.get("surveyed_commits")
        if not isinstance(surveyed_commits, dict):
            missing.append("closure_manifest:survey_provenance:surveyed_commits")
        else:
            for lane_name, rel_path in SURVEY_MANIFEST_PATHS.items():
                survey_manifest = load_json(root, rel_path)
                if not isinstance(survey_manifest, dict):
                    missing.append(f"{rel_path}:type")
                    continue
                expected_commit = survey_manifest.get("surveyed_commit")
                actual_commit = surveyed_commits.get(lane_name)
                if actual_commit != expected_commit:
                    missing.append(f"closure_manifest:survey_provenance:surveyed_commits:{lane_name}")

    scoreboard = closure_manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing.append("closure_manifest:roadmap_parity_scoreboard")
    else:
        for key, expected_evidence in EXPECTED_SCOREBOARD_EVIDENCE.items():
            entry = scoreboard.get(key)
            if not isinstance(entry, dict):
                missing.append(f"closure_manifest:roadmap_parity_scoreboard:{key}")
                continue
            if entry.get("evidence") != expected_evidence:
                missing.append(f"closure_manifest:roadmap_parity_scoreboard:{key}:evidence")

    ledger_text = read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md")
    for marker in LEDGER_MARKERS:
        if marker not in ledger_text:
            missing.append(f"ledger:{marker}")

    mmio_survey_text = read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md")
    for marker in MMIO_SURVEY_MARKERS:
        if marker not in mmio_survey_text:
            missing.append(f"mmio_survey:{marker}")

    return [], missing


def write_fixture(root: Path) -> None:
    closure_manifest = {
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": EXPECTED_LANE_KEYS,
            "surveyed_commits": {
                "core": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
                "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
                "input": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
                "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
            },
        },
        "roadmap_parity_scoreboard": {
            key: {"evidence": value} for key, value in EXPECTED_SCOREBOARD_EVIDENCE.items()
        },
    }

    survey_manifests = {
        SURVEY_MANIFEST_PATHS["core"]: {"surveyed_commit": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21"},
        SURVEY_MANIFEST_PATHS["ring"]: {"surveyed_commit": "fe8a43ea2e186da0da152198b571dff57ea3c38c"},
        SURVEY_MANIFEST_PATHS["input"]: {"surveyed_commit": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38"},
        SURVEY_MANIFEST_PATHS["mmio"]: {"surveyed_commit": "0945df1cf664a3582d7241f859183a13f3f04adb"},
    }

    text_files = {
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == "zigux/tests/phase10_closure_manifest.json":
            path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        elif rel_path in survey_manifests:
            path.write_text(json.dumps(survey_manifests[rel_path], indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(text_files.get(rel_path, "fixture\n"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-freeze-self-test:{label}:missing_files:{','.join(missing_files)}")
    if marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-freeze-self-test:{label}:expected:{marker}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_freeze_") as tmp_dir:
        fixture_root = Path(tmp_dir) / "repo"
        write_fixture(fixture_root)

        missing_files, missing_markers = validate(fixture_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-freeze-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = fixture_root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"].pop()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "scoreboard_evidence_guard",
            fixture_root,
            "closure_manifest:roadmap_parity_scoreboard:mmio_wrappers:evidence",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["surveyed_commits"]["core"] = "deadbeef"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "survey_commit_guard",
            fixture_root,
            "closure_manifest:survey_provenance:surveyed_commits:core",
        )
        write_fixture(fixture_root)

        ledger_path = fixture_root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        ledger_path.write_text("missing\n", encoding="utf-8")
        expect_missing_marker(
            "ledger_marker_guard",
            fixture_root,
            "ledger:PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
        )
        write_fixture(fixture_root)

        survey_path = fixture_root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        survey_path.write_text("missing\n", encoding="utf-8")
        expect_missing_marker(
            "mmio_note_guard",
            fixture_root,
            "mmio_survey:PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
        )

    print("PHASE10_FREEZE_BOUNDARY_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_FREEZE_BOUNDARY_VALIDATOR_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_FREEZE_BOUNDARY_VALIDATION=fail")
    print("MISSING_PHASE10_FREEZE_BOUNDARY_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_FREEZE_BOUNDARY_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_FREEZE_BOUNDARY_VALIDATION=fail")
    print("MISSING_PHASE10_FREEZE_BOUNDARY_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_FREEZE_BOUNDARY_MARKERS_END")
    sys.exit(1)

print("PHASE10_FREEZE_BOUNDARY_VALIDATION=pass")
print(f"PHASE10_FREEZE_BOUNDARY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE10_FREEZE_BOUNDARY_REQUIRED_MARKER_COUNT="
    f"{len(LEDGER_MARKERS) + len(MMIO_SURVEY_MARKERS)}"
)
