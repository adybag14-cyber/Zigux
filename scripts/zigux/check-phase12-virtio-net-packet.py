#!/usr/bin/env python3
"""Fail-closed checker for the active Phase 12 virtio_net packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_VIRTIO_NET_PACKET"

MANIFEST_PATH = Path("zigux/tests/phase12_virtio_net_manifest.json")
SURVEY_NOTE_PATH = Path("Documentation/zigux/phase12-virtio-net-survey.md")
QUEUE_RESUME_PATH = Path("zigux/tests/phase12_virtio_net_queue_resume.zig")
TRANSMIT_RECYCLE_PATH = Path("zigux/tests/phase12_virtio_net_transmit_recycle.zig")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

SURVEY_NOTE_MARKERS = (
    "PHASE12_SLICE=virtio-net-survey",
    "queue-resume",
    "mergeable-buffer-length",
    "runtime data-path",
)

QUEUE_RESUME_MARKERS = (
    "phase12 virtio net queue resume keeps mergeable replay and throughput guard explicit",
    "phase12 virtio net queue resume keeps control replay markers explicit",
    "throughput_guard_active",
    "after_control_queue_restore",
)

TRANSMIT_RECYCLE_MARKERS = (
    "phase12 virtio net transmit recycle keeps a stopped queue parked while a bounded poll leaves completion backlog",
    "requires_followup_recycle",
    "wakes_transmit_queue",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "virtio_net_queue_resume_root_module",
    "run_virtio_net_queue_resume_tests",
    "phase12_virtio_net_transmit_recycle.zig",
    "virtio_net_transmit_recycle_root_module",
    "run_virtio_net_transmit_recycle_tests",
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
)

MAKEFILE_MARKERS = (
    "PHONY += phase12-validate phase12-smoke",
    "PHONY += phase12-test phase12",
    "phase12-smoke:",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
)


class CheckFailure(RuntimeError):
    """Raised when the packet checker finds drift."""


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, relative_path: Path, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{relative_path} missing marker: {marker}")


def check_manifest(root: Path) -> int:
    manifest_text = read_text(root, MANIFEST_PATH)
    manifest = json.loads(manifest_text)

    if manifest.get("lane_key") != "P12-L02":
        raise CheckFailure("virtio_net manifest lane_key is not P12-L02")
    if manifest.get("phase") != "Phase 12":
        raise CheckFailure("virtio_net manifest phase is not Phase 12")
    if manifest.get("anchor") != "drivers/net/virtio_net.c":
        raise CheckFailure("virtio_net manifest anchor drifted")
    if manifest.get("survey_path") != "zigux/tests/phase12_virtio_net_survey.zig":
        raise CheckFailure("virtio_net manifest survey_path drifted")

    surveyed_commit = manifest.get("surveyed_commit", "")
    if len(surveyed_commit) != 40 or any(ch not in "0123456789abcdef" for ch in surveyed_commit):
        raise CheckFailure("virtio_net manifest surveyed_commit is not a 40-char lowercase hex sha")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckFailure("virtio_net manifest gaps field is not a list")

    gap_map = {}
    for gap in gaps:
        if isinstance(gap, dict) and isinstance(gap.get("id"), str):
            gap_map[gap["id"]] = gap

    required_gap_ids = (
        "phase12-virtio-net-survey",
        "phase12-virtio-net-queue-recovery-followup",
        "phase12-virtio-net-queue-resume-summary",
        "phase12-virtio-net-receive-path-summary",
        "phase12-virtio-net-mergeable-refill-summary",
        "phase12-virtio-net-mergeable-buffer-length-summary",
        "phase12-virtio-net-runtime-data-path",
    )
    for gap_id in required_gap_ids:
        if gap_id not in gap_map:
            raise CheckFailure(f"virtio_net manifest missing gap: {gap_id}")

    runtime_gap = gap_map["phase12-virtio-net-runtime-data-path"]
    runtime_status = runtime_gap.get("status")
    if runtime_status not in {"blocked_on_dma_transport", "blocked", "deferred_high_risk"}:
        raise CheckFailure("virtio_net runtime-data-path gap lost its blocked posture")

    return len(gaps)


def check_packet(root: Path) -> int:
    gap_count = check_manifest(root)
    require_markers(read_text(root, SURVEY_NOTE_PATH), SURVEY_NOTE_PATH, SURVEY_NOTE_MARKERS)
    require_markers(read_text(root, QUEUE_RESUME_PATH), QUEUE_RESUME_PATH, QUEUE_RESUME_MARKERS)
    require_markers(
        read_text(root, TRANSMIT_RECYCLE_PATH),
        TRANSMIT_RECYCLE_PATH,
        TRANSMIT_RECYCLE_MARKERS,
    )
    require_markers(read_text(root, BUILD_PATH), BUILD_PATH, BUILD_MARKERS)
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_PATH, MAKEFILE_MARKERS)
    return gap_count


def write_fixture(root: Path) -> None:
    fixture_files = {
        MANIFEST_PATH: json.dumps(
            {
                "lane_key": "P12-L02",
                "phase": "Phase 12",
                "surveyed_commit": "0123456789abcdef0123456789abcdef01234567",
                "anchor": "drivers/net/virtio_net.c",
                "survey_path": "zigux/tests/phase12_virtio_net_survey.zig",
                "gaps": [
                    {"id": "phase12-virtio-net-survey", "status": "starter_landed"},
                    {"id": "phase12-virtio-net-queue-recovery-followup", "status": "starter_landed"},
                    {"id": "phase12-virtio-net-queue-resume-summary", "status": "starter_landed"},
                    {"id": "phase12-virtio-net-receive-path-summary", "status": "starter_landed"},
                    {"id": "phase12-virtio-net-mergeable-refill-summary", "status": "starter_landed"},
                    {
                        "id": "phase12-virtio-net-mergeable-buffer-length-summary",
                        "status": "starter_landed",
                    },
                    {
                        "id": "phase12-virtio-net-runtime-data-path",
                        "status": "blocked_on_dma_transport",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        SURVEY_NOTE_PATH: "\n".join(
            [
                "# Phase 12 Virtio Net Survey",
                "PHASE12_SLICE=virtio-net-survey",
                "queue-resume",
                "mergeable-buffer-length",
                "runtime data-path",
            ]
        )
        + "\n",
        QUEUE_RESUME_PATH: "\n".join(QUEUE_RESUME_MARKERS) + "\n",
        TRANSMIT_RECYCLE_PATH: "\n".join(TRANSMIT_RECYCLE_MARKERS) + "\n",
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
    }

    for relative_path, text in fixture_files.items():
        absolute_path = root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_fixture(root)

        check_packet(root)
        cases += 1

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P12-L04"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_packet(root)
        except CheckFailure as exc:
            if "lane_key" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected lane-key drift to fail")

        write_fixture(root)
        queue_resume_path = root / QUEUE_RESUME_PATH
        queue_resume_path.write_text("throughput_guard_active\n", encoding="utf-8")
        try:
            check_packet(root)
        except CheckFailure as exc:
            if "missing marker" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected queue-resume drift to fail")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        gap_count = check_packet(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_GAP_COUNT={gap_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
