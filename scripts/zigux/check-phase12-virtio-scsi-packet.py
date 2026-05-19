#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_packet

Fail-closed checker for the bounded Phase 12 virtio_scsi survey packet.
It keeps the slice note, survey manifest, fallback catalog, and shared
Phase 12 support-bundle reminder aligned around current repo reality.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_packet"

SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
FALLBACK_CATALOG_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
SURVEY_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_NOTE_PATH,
    FALLBACK_CATALOG_PATH,
    SURVEY_MANIFEST_PATH,
    PHASE12_BUILD_PATH,
    MAKEFILE_PATH,
]

SLICE_MARKERS = [
    "# Phase 12 virtio_scsi Slice",
    "`PHASE12_SLICE=virtio-scsi-queue-lab-support`",
    "- lane: `complex-drivers-infra`",
    "- `zigux/tests/phase12_virtio_scsi_manifest.json` keeps the lane key, surveyed commit, shipped paths, and direct validation commands machine-checkable for the current survey packet",
    "- `zigux/tests/phase12_build.zig` now acts as a shared Phase 12 support-bundle surface only: current `master` wires the `virtio_net` queue-resume, transmit-recycle, post-reset replay, and throughput-parity tests through the shared `smoke` and `test` steps, while the `virtio_scsi` direct replay, syntax-lab, repeated-replan gate, repeated-rollback gate, and survey gate remain lane-local validation surfaces",
    "- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the survey manifest, slice note, or support-bundle reminder drifts",
    "## Repo-reality boundaries",
    "- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap",
    "- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head",
]

FORBIDDEN_SLICE_MARKERS = [
    "phase12_virtio_scsi_packet.zig",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
]

SURVEY_MANIFEST_MARKERS = [
    '"lane_key": "P12-L13"',
    '"verified_on": "2026-05-19"',
    '"preexisting_phase12_support_packet_present": false',
    '"preexisting_phase12_support_manifest_present": true',
    '"status": "lane_local_validation_present_shared_build_missing"',
    '"status": "lane_local_validation_present"',
    '"status": "support_packet_removed_survey_manifest_present"',
]

FALLBACK_CATALOG_MARKERS = [
    "- exact coverage evidence refreshed on `2026-05-19` against live current `master`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py` -> blob `a2477ccf64a6874768662d5e8dae1b2b19c88371`",
    "`scripts/zigux/README.md` -> blob `5b066d41b80c380e516b3c6afd878b85af593800`",
    "`zigux/tests/phase12_build.zig` blob `db74940c2581c6953948a7b6277af58f10498f72` currently wires only the `virtio_net` queue-resume, transmit-recycle, post-reset replay, and throughput-parity tests through both shared `smoke` and shared `test`",
    "current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane",
    "historical fallback snapshot for the pinned raw-read packet",
]

FORBIDDEN_FALLBACK_MARKERS = [
    "phase12_virtio_scsi_packet.zig",
    "phase12_virtio_scsi_packet.py",
    "18a1f2bfbb78a7c3b871fba93b33f88cacf710d7",
]

MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-smoke phase12-test",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def forbid_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden stale marker in {rel_path}: {marker}")


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


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

    slice_text = read_text(root / SLICE_PATH)
    require_markers(errors, SLICE_PATH, slice_text, SLICE_MARKERS)
    forbid_markers(errors, SLICE_PATH, slice_text, FORBIDDEN_SLICE_MARKERS)

    fallback_text = read_text(root / FALLBACK_CATALOG_PATH)
    require_markers(errors, FALLBACK_CATALOG_PATH, fallback_text, FALLBACK_CATALOG_MARKERS)
    forbid_markers(errors, FALLBACK_CATALOG_PATH, fallback_text, FORBIDDEN_FALLBACK_MARKERS)

    require_markers(
        errors,
        SURVEY_MANIFEST_PATH,
        read_text(root / SURVEY_MANIFEST_PATH),
        SURVEY_MANIFEST_MARKERS,
    )
    require_markers(errors, MAKEFILE_PATH, read_text(root / MAKEFILE_PATH), MAKEFILE_MARKERS)
    return errors


def good_slice_text() -> str:
    return "\n".join(
        [
            "# Phase 12 virtio_scsi Slice",
            "- `PHASE12_SLICE=virtio-scsi-queue-lab-support`",
            "- lane: `complex-drivers-infra`",
            "- `zigux/tests/phase12_virtio_scsi_manifest.json` keeps the lane key, surveyed commit, shipped paths, and direct validation commands machine-checkable for the current survey packet",
            "- `zigux/tests/phase12_build.zig` now acts as a shared Phase 12 support-bundle surface only: current `master` wires the `virtio_net` queue-resume, transmit-recycle, post-reset replay, and throughput-parity tests through the shared `smoke` and `test` steps, while the `virtio_scsi` direct replay, syntax-lab, repeated-replan gate, repeated-rollback gate, and survey gate remain lane-local validation surfaces",
            "- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the survey manifest, slice note, or support-bundle reminder drifts",
            "",
            "## Repo-reality boundaries",
            "- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap",
            "- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head",
            "",
        ]
    )


def good_fallback_catalog_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog",
            "",
            "## Current-Master Evidence Snapshot",
            *FALLBACK_CATALOG_MARKERS,
            "",
        ]
    )


def good_survey_manifest_text() -> str:
    return "\n".join(
        [
            "{",
            '  "lane_key": "P12-L13",',
            '  "verified_on": "2026-05-19",',
            '  "survey_summary": {',
            '    "preexisting_phase12_support_packet_present": false,',
            '    "preexisting_phase12_support_manifest_present": true',
            "  },",
            '  "gaps": [',
            '    { "status": "lane_local_validation_present_shared_build_missing" },',
            '    { "status": "lane_local_validation_present" },',
            '    { "status": "support_packet_removed_survey_manifest_present" }',
            "  ]",
            "}",
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            ".PHONY: phase12-smoke phase12-test phase12",
            "phase12-smoke:",
            "\t@true",
            "phase12-test:",
            "\t@true",
            "phase12: phase12-smoke phase12-test",
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    write_text(root / SLICE_PATH, good_slice_text())
    write_text(root / SURVEY_NOTE_PATH, "# Phase 12 Virtio SCSI Survey\n")
    write_text(root / FALLBACK_CATALOG_PATH, good_fallback_catalog_text())
    write_text(root / SURVEY_MANIFEST_PATH, good_survey_manifest_text())
    write_text(root / PHASE12_BUILD_PATH, "// phase12 build fixture\n")
    write_text(root / MAKEFILE_PATH, good_makefile_text())


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-virtio-scsi-packet-"))
    try:
        write_fixture_tree(tmp_root)
        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text().replace(SLICE_MARKERS[5] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SLICE_MARKERS[5],
            "missing slice checker marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text().replace(SLICE_MARKERS[7] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SLICE_MARKERS[7],
            "missing nvme boundary marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text() + FORBIDDEN_SLICE_MARKERS[0] + "\n",
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FORBIDDEN_SLICE_MARKERS[0],
            "stale support-packet marker not rejected",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / FALLBACK_CATALOG_PATH,
            good_fallback_catalog_text().replace(
                FALLBACK_CATALOG_MARKERS[3] + "\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FALLBACK_CATALOG_MARKERS[3],
            "missing fallback evidence marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / FALLBACK_CATALOG_PATH,
            good_fallback_catalog_text() + FORBIDDEN_FALLBACK_MARKERS[0] + "\n",
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FORBIDDEN_FALLBACK_MARKERS[0],
            "stale fallback marker not rejected",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SURVEY_MANIFEST_PATH,
            good_survey_manifest_text().replace(
                SURVEY_MANIFEST_MARKERS[-1],
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SURVEY_MANIFEST_MARKERS[-1],
            "missing survey-manifest status",
        )

        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 virtio_scsi survey packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
