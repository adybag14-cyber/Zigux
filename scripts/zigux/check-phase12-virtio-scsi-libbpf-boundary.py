#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary

Fail-closed checker for the exact Phase 12 boundary between the rollback-only
`virtio_scsi` survey packet and the adjacent parked libbpf segment packet.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary"

VIRTIO_SCSI_SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
VIRTIO_SCSI_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
VIRTIO_SCSI_FIXTURE_MANIFEST_PATH = "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
VIRTIO_SCSI_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
VIRTIO_SCSI_SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
COMPLEX_DRIVER_NOTE_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_VERIFY_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
LIBBPF_HEAVY_CONSUMER_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)

REQUIRED_FILES = [
    VIRTIO_SCSI_SLICE_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
    VIRTIO_SCSI_FIXTURE_MANIFEST_PATH,
    VIRTIO_SCSI_MANIFEST_PATH,
    VIRTIO_SCSI_SURVEY_GATE_PATH,
    COMPLEX_DRIVER_NOTE_PATH,
    LIBBPF_SURVEY_PATH,
    LIBBPF_VERIFY_NOTE_PATH,
    LIBBPF_HEAVY_CONSUMER_PATH,
]

REQUIRED_MARKERS = {
    VIRTIO_SCSI_SURVEY_PATH: [
        "PHASE12_STATUS=rollback-evidence-only-live-starter-missing",
        "PHASE12_LANE=P12-L13",
        "rollback-only split machine-checkable",
    ],
    VIRTIO_SCSI_FIXTURE_MANIFEST_PATH: [
        '"lane_key": "P12-L13"',
        '"fixture_kind": "rollback_evidence_presence_manifest"',
        '"source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json"',
        '"driver-local starter and replay gates are absent"',
    ],
    VIRTIO_SCSI_MANIFEST_PATH: [
        '"lane_key": "P12-L13"',
        '"preexisting_phase12_direct_test_present": false',
        '"phase12-virtio-scsi-runtime-request-flow"',
    ],
    VIRTIO_SCSI_SURVEY_GATE_PATH: [
        'test "phase12 virtio scsi survey manifest keeps the rollback-only packet truthful"',
        'pathExists("drivers/scsi/virtio_scsi.zig")',
        'Documentation/zigux/phase12-virtio-scsi-survey.md',
    ],
    COMPLEX_DRIVER_NOTE_PATH: [
        "current `master` now keeps the bounded `virtio_scsi` packet readable only through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py`, while `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` remain absent on current `master`",
        "keep those `virtio_scsi` survey, fallback, fixture, manifest, and checker surfaces framed as rollback-evidence-only driver-local packet truth",
        "shared PMO companions such as `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` may therefore keep only the rollback-evidence `virtio_scsi` survey companions explicit as current driver-local packet members",
    ],
    LIBBPF_SURVEY_PATH: [
        "current `master` still exposes a bounded directly readable `zigux_segments` footing",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "older `manifest.json` catalog is no longer directly readable on current `master`",
    ],
    LIBBPF_VERIFY_NOTE_PATH: [
        "`tools/lib/bpf/zigux_segments/verify.zig` is directly readable on current `master`",
        "the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
    ],
}

FORBIDDEN_MARKERS = {
    COMPLEX_DRIVER_NOTE_PATH: [
        "current `master` now directly rematerializes the bounded `virtio_scsi` rollback-lab packet through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`",
    ],
    LIBBPF_VERIFY_NOTE_PATH: [
        "the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
    ],
}


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel_path)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root / rel_path)
        for marker in markers:
            if marker in text:
                errors.append(f"forbidden marker in {rel_path}: {marker}")

    return errors


def write_fixture_tree(root: Path) -> None:
    fixture_text = {
        VIRTIO_SCSI_SLICE_PATH: "# Phase 12 virtio_scsi Slice\n- `PHASE12_SLICE=virtio-scsi-rollback-evidence`\n",
        VIRTIO_SCSI_SURVEY_PATH: "# Phase 12 Virtio SCSI Survey\nPHASE12_STATUS=rollback-evidence-only-live-starter-missing\nPHASE12_LANE=P12-L13\nrollback-only split machine-checkable\n",
        VIRTIO_SCSI_FALLBACK_PATH: "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog\n",
        VIRTIO_SCSI_FIXTURE_MANIFEST_PATH: '{\n  "lane_key": "P12-L13",\n  "fixture_kind": "rollback_evidence_presence_manifest",\n  "source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json",\n  "scope": "driver-local starter and replay gates are absent"\n}\n',
        VIRTIO_SCSI_MANIFEST_PATH: '{\n  "lane_key": "P12-L13",\n  "preexisting_phase12_direct_test_present": false,\n  "gaps": ["phase12-virtio-scsi-runtime-request-flow"]\n}\n',
        VIRTIO_SCSI_SURVEY_GATE_PATH: 'test "phase12 virtio scsi survey manifest keeps the rollback-only packet truthful" {\n    _ = pathExists("drivers/scsi/virtio_scsi.zig");\n    _ = "Documentation/zigux/phase12-virtio-scsi-survey.md";\n}\n',
        COMPLEX_DRIVER_NOTE_PATH: "current `master` now keeps the bounded `virtio_scsi` packet readable only through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py`, while `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` remain absent on current `master`\nkeep those `virtio_scsi` survey, fallback, fixture, manifest, and checker surfaces framed as rollback-evidence-only driver-local packet truth\nshared PMO companions such as `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` may therefore keep only the rollback-evidence `virtio_scsi` survey companions explicit as current driver-local packet members\n",
        LIBBPF_SURVEY_PATH: "current `master` still exposes a bounded directly readable `zigux_segments` footing\n`tools/lib/bpf/zigux_segments/verify.zig`\nolder `manifest.json` catalog is no longer directly readable on current `master`\n",
        LIBBPF_VERIFY_NOTE_PATH: "`tools/lib/bpf/zigux_segments/verify.zig` is directly readable on current `master`\nthe direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`\n",
        LIBBPF_HEAVY_CONSUMER_PATH: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing\n",
    }
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text[rel_path])


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-virtio-scsi-libbpf-boundary-"))
    try:
        write_fixture_tree(tmp_root)
        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / VIRTIO_SCSI_FIXTURE_MANIFEST_PATH,
            read_text(tmp_root / VIRTIO_SCSI_FIXTURE_MANIFEST_PATH).replace(
                "rollback_evidence_presence_manifest",
                "rollback_presence_manifest",
                1,
            ),
        )
        if not any(
            "missing marker in" in error and VIRTIO_SCSI_FIXTURE_MANIFEST_PATH in error
            for error in check(tmp_root, source_text=MARKER)
        ):
            raise SystemExit("expected fixture-manifest marker failure")

        write_fixture_tree(tmp_root)
        write_text(tmp_root / COMPLEX_DRIVER_NOTE_PATH, read_text(tmp_root / COMPLEX_DRIVER_NOTE_PATH).replace("rollback-evidence-only", "rollback-lab", 1))
        if not any("missing marker in" in error and COMPLEX_DRIVER_NOTE_PATH in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("expected complex-driver marker failure")

        write_fixture_tree(tmp_root)
        write_text(tmp_root / COMPLEX_DRIVER_NOTE_PATH, read_text(tmp_root / COMPLEX_DRIVER_NOTE_PATH) + FORBIDDEN_MARKERS[COMPLEX_DRIVER_NOTE_PATH][0] + "\n")
        if not any("forbidden marker in" in error and COMPLEX_DRIVER_NOTE_PATH in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("expected complex-driver forbidden-marker failure")

        write_fixture_tree(tmp_root)
        write_text(tmp_root / LIBBPF_VERIFY_NOTE_PATH, read_text(tmp_root / LIBBPF_VERIFY_NOTE_PATH).replace("file_path_handle_bridge.zig", "file_path_handle_bridge_absent.zig", 1))
        if not any("missing marker in" in error and LIBBPF_VERIFY_NOTE_PATH in error for error in check(tmp_root, source_text=MARKER)):
            raise SystemExit("expected libbpf verify-note marker failure")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=repo_root())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY=fail")
        for error in errors:
            print(error)
        return 1

    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
