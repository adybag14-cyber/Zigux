#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary

Fail-closed checker for the shared Phase 12 boundary between the shipped
`virtio_scsi` recovery packet and the parked libbpf verify-shard packet.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary"

RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_COORDINATION_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_VERIFY_SHARD_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
LIBBPF_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
VIRTIO_SCSI_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)

REQUIRED_FILES = [
    RELEASE_READINESS_PATH,
    RELEASE_COORDINATION_PATH,
    LIBBPF_SURVEY_PATH,
    LIBBPF_VERIFY_SHARD_PATH,
    LIBBPF_LANE_PATH,
    SNAPSHOT_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
]

REQUIRED_MARKERS = {
    RELEASE_READINESS_PATH: [
        "the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor",
        "the shipped `phase12-validate` support bundle",
    ],
    RELEASE_COORDINATION_PATH: [
        "keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, "
        "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and "
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` aligned around the same "
        "shared Phase 12 libbpf posture",
        "keep `Documentation/zigux/phase12-virtio-scsi-slice.md`, "
        "`Documentation/zigux/phase12-virtio-scsi-survey.md`, "
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, "
        "`zigux/tests/phase12_virtio_scsi_manifest.json`, "
        "`zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, "
        "`zigux/tests/phase12_virtio_scsi.zig`, "
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, "
        "`zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, "
        "`zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and "
        "`zigux/tests/phase12_virtio_scsi_packet.zig` aligned with the shared "
        "smoke-first replay packet",
    ],
    LIBBPF_SURVEY_PATH: [
        "the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor "
        "keeps that broader parked reviewability packet visible",
        "the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, "
        "`zigux/Makefile`, and the active driver-facing release order described by the "
        "Phase 12 PMO notes",
    ],
    LIBBPF_VERIFY_SHARD_PATH: [
        "the shared Phase 12 checker still only enforces the shipped docs, workflow, "
        "Makefile, and `virtio_scsi` plus starter-present `virtio_net` smoke-first build packet",
        "the direct `phase12_libbpf_*` replay files plus "
        "`tools/lib/bpf/zigux_segments/verify.zig` and "
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` should stay described "
        "as note-owned or snapshot-backed boundaries",
    ],
    LIBBPF_LANE_PATH: [
        "keep the shared libbpf packet explicit through "
        "`Documentation/zigux/phase12-libbpf-segment-survey.md`, "
        "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and the still-present "
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor",
        "leave driver-local replay and survey evolution to the separate complex-driver "
        "companion and the concrete `nvme_pci`, `virtio_net`, or `virtio_scsi` packet that changes",
    ],
    VIRTIO_SCSI_SURVEY_PATH: [
        "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "phase12_virtio_scsi_repeated_rollback_gate.zig",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- `make -C zigux phase12-validate`",
    ],
    SNAPSHOT_PATH: [
        "\"surveyed_commit\"",
    ],
}


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel}")
    if errors:
        return errors

    checker_text = source_text if source_text is not None else Path(__file__).read_text(encoding="utf-8")
    if MARKER not in checker_text:
        errors.append("checker marker missing from checker source")

    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                errors.append(
                    f"marker count drift in {rel}: {marker} (expected 1, found {count})"
                )

    return errors


def write_fixture_root(root: Path) -> None:
    fixture_text = {
        RELEASE_READINESS_PATH: "\n".join(REQUIRED_MARKERS[RELEASE_READINESS_PATH]) + "\n",
        RELEASE_COORDINATION_PATH: "\n".join(REQUIRED_MARKERS[RELEASE_COORDINATION_PATH]) + "\n",
        LIBBPF_SURVEY_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_SURVEY_PATH]) + "\n",
        LIBBPF_VERIFY_SHARD_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_VERIFY_SHARD_PATH]) + "\n",
        LIBBPF_LANE_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_LANE_PATH]) + "\n",
        SNAPSHOT_PATH: "{\n  \"surveyed_commit\": \"fixture\"\n}\n",
        VIRTIO_SCSI_SURVEY_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_SURVEY_PATH]) + "\n",
        VIRTIO_SCSI_FALLBACK_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_FALLBACK_PATH]) + "\n",
    }

    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text[rel], encoding="utf-8")


def mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase12_vscsi_libbpf_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        assert check(root, source_text=MARKER) == []

        missing_target = root / LIBBPF_SURVEY_PATH
        missing_target.unlink()
        errors = check(root, source_text=MARKER)
        assert errors == [f"missing file: {LIBBPF_SURVEY_PATH}"]
        write_fixture_root(root)

        marker = REQUIRED_MARKERS[RELEASE_COORDINATION_PATH][0]
        mutate(root, RELEASE_COORDINATION_PATH, marker, "broken marker")
        errors = check(root, source_text=MARKER)
        assert errors == [
            f"marker count drift in {RELEASE_COORDINATION_PATH}: {marker} (expected 1, found 0)"
        ]

    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shipped Phase 12 virtio_scsi recovery packet and the parked "
            "libbpf verify-shard packet stay clearly separated on current master."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    errors = check(repo_root())
    if errors:
        print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY=fail")
        print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_ERRORS_END")
        return 1

    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY=pass")
    print(f"PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
