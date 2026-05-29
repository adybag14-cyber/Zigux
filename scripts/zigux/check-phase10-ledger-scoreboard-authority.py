"""Fail closed when the Phase 10 ledger loses manifest-backed scoreboard authority."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
LEDGER_PATH = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"

RETAINED_SCOREBOARD_HEADING = "Manifest-backed scoreboard refreshes retained here for the shared checker route:"
REQUIRED_SCOREBOARD_ROWS = (
    (
        "virtqueue_wrappers",
        "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE",
        (
            "drivers/virtio/virtio_ring_registration_summary.zig",
            "drivers/virtio/virtio_ring_used_buffer_poll.zig",
        ),
    ),
    (
        "lab_only_driver_validation",
        "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE",
        (
            "zigux/tests/phase10_virtio_ring_queue_build.zig",
            "drivers/virtio/virtio_input_registration_preflight.zig",
            "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
        ),
    ),
)


def read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def expected_scoreboard_line(manifest: dict, row_name: str, ledger_key: str) -> str:
    scoreboard = manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        raise ValueError("roadmap_parity_scoreboard missing from closure manifest")
    row = scoreboard.get(row_name)
    if not isinstance(row, dict):
        raise ValueError(f"roadmap_parity_scoreboard.{row_name} missing from closure manifest")
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise ValueError(f"roadmap_parity_scoreboard.{row_name}.evidence is not a string list")
    return f"- `{ledger_key}={','.join(evidence)}`"


def collect_drift(root: Path) -> list[str]:
    manifest = read_manifest(root)
    ledger_text = (root / LEDGER_PATH).read_text(encoding="utf-8")
    drift: list[str] = []
    if RETAINED_SCOREBOARD_HEADING not in ledger_text:
        drift.append("ledger:manifest_backed_scoreboard_heading:missing")
    for row_name, ledger_key, required_paths in REQUIRED_SCOREBOARD_ROWS:
        line = expected_scoreboard_line(manifest, row_name, ledger_key)
        if line not in ledger_text:
            drift.append(f"ledger:{ledger_key}:manifest_exact_line:missing")
        for path in required_paths:
            if path not in line:
                drift.append(f"manifest:{row_name}:{path}:missing")
            if path not in ledger_text:
                drift.append(f"ledger:{ledger_key}:{path}:missing")
    return drift


def write_sample_root(root: Path, *, missing_heading: bool = False, stale_virtqueue: bool = False) -> None:
    manifest = {
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {
                "evidence": [
                    "drivers/virtio/virtio_ring.zig",
                    "drivers/virtio/virtio_ring_publish_readiness.zig",
                    "drivers/virtio/virtio_ring_registration_summary.zig",
                    "drivers/virtio/virtio_ring_used_buffer_poll.zig",
                    "zigux/tests/phase10_virtio_ring.zig",
                    "zigux/tests/phase10_virtio_ring_manifest.json",
                    "Documentation/zigux/phase10-virtio-ring-survey.md",
                ],
            },
            "lab_only_driver_validation": {
                "evidence": [
                    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                    "zigux/tests/phase10_build.zig",
                    "zigux/tests/phase10_virtio_ring_queue_build.zig",
                    "drivers/virtio/virtio_input_registration_preflight.zig",
                    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
                ],
            },
        },
    }
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    virtqueue_line = expected_scoreboard_line(
        manifest,
        "virtqueue_wrappers",
        "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE",
    )
    if stale_virtqueue:
        virtqueue_line = "- `PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=drivers/virtio/virtio_ring.zig`"
    lab_line = expected_scoreboard_line(
        manifest,
        "lab_only_driver_validation",
        "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE",
    )
    heading = "" if missing_heading else RETAINED_SCOREBOARD_HEADING + "\n"
    ledger_path = root / LEDGER_PATH
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(f"# Phase 10 Closure Ledger\n\n{heading}{virtqueue_line}\n{lab_line}\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "ok"
        write_sample_root(root)
        assert collect_drift(root) == []
        no_heading = Path(tmp) / "no_heading"
        write_sample_root(no_heading, missing_heading=True)
        assert "ledger:manifest_backed_scoreboard_heading:missing" in collect_drift(no_heading)
        stale = Path(tmp) / "stale"
        write_sample_root(stale, stale_virtqueue=True)
        drift = collect_drift(stale)
        assert "ledger:PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE:manifest_exact_line:missing" in drift
        assert "ledger:PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE:drivers/virtio/virtio_ring_registration_summary.zig:missing" in drift
    print("PHASE10_LEDGER_SCOREBOARD_AUTHORITY_SELF_TEST=pass")
    print("PHASE10_LEDGER_SCOREBOARD_AUTHORITY_SELF_TEST_CASE_COUNT=3")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        return 0
    drift = collect_drift(args.root)
    if drift:
        for item in drift:
            print(f"PHASE10_LEDGER_SCOREBOARD_AUTHORITY_DRIFT={item}")
        return 1
    print("PHASE10_LEDGER_SCOREBOARD_AUTHORITY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
