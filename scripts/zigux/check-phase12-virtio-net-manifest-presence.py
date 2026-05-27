#!/usr/bin/env python3
"""Fail-closed checker for Phase 12 virtio_net manifest presence drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REQUIRED_PRESENCE_FLAGS = {
    "preexisting_phase10_build_present": "zigux/tests/phase10_build.zig",
    "preexisting_virtio_core_zig_present": "drivers/virtio/virtio.zig",
    "preexisting_virtio_ring_zig_present": "drivers/virtio/virtio_ring.zig",
    "preexisting_virtio_input_zig_present": "drivers/virtio/virtio_input.zig",
    "preexisting_phase12_build_present": "zigux/tests/phase12_build.zig",
    "preexisting_phase12_virtio_net_survey_present": "zigux/tests/phase12_virtio_net_survey.zig",
    "preexisting_phase12_survey_note_present": "Documentation/zigux/phase12-virtio-net-survey.md",
    "preexisting_virtio_net_queue_resume_zig_present": "drivers/net/virtio_net_queue_resume.zig",
    "preexisting_virtio_net_receive_refill_replay_zig_present": "drivers/net/virtio_net_receive_refill_replay.zig",
    "preexisting_virtio_net_transmit_recycle_zig_present": "drivers/net/virtio_net_transmit_recycle.zig",
    "preexisting_virtio_net_post_reset_replay_zig_present": "drivers/net/virtio_net_post_reset_replay.zig",
    "preexisting_virtio_net_throughput_parity_zig_present": "drivers/net/virtio_net_throughput_parity.zig",
    "preexisting_phase12_virtio_net_queue_resume_present": "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "preexisting_phase12_virtio_net_receive_refill_replay_present": "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "preexisting_phase12_virtio_net_transmit_recycle_present": "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "preexisting_phase12_virtio_net_post_reset_replay_present": "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "preexisting_phase12_virtio_net_throughput_parity_present": "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "preexisting_virtio_net_zig_present": "drivers/net/virtio_net.zig",
    "preexisting_phase12_virtio_net_zig_present": "zigux/tests/phase12_virtio_net.zig",
    "preexisting_phase12_virtio_net_syntax_lab_present": "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "preexisting_phase12_virtio_net_syntax_lab_build_present": "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
}


def load_manifest(root: Path) -> dict:
    manifest_path = root / "zigux/tests/phase12_virtio_net_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_manifest_presence(root: Path) -> tuple[list[str], int]:
    manifest = load_manifest(root)
    summary = manifest.get("survey_summary", {})
    failures: list[str] = []

    for field, rel_path in REQUIRED_PRESENCE_FLAGS.items():
        expected = summary.get(field)
        if not isinstance(expected, bool):
            failures.append(f"{field}: expected boolean field in survey_summary")
            continue

        actual = (root / rel_path).is_file()
        if actual != expected:
            failures.append(
                f"{field}: manifest says {expected!s} for {rel_path}, "
                f"but filesystem presence is {actual!s}"
            )

    return failures, len(REQUIRED_PRESENCE_FLAGS)


def run_live_check(root: Path) -> int:
    failures, checked = check_manifest_presence(root)
    if failures:
        print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE=fail")
        print(f"PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_CHECKED={checked}")
        print(f"PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_FAILURES={len(failures)}")
        for failure in failures:
            print(f"PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_DETAIL={failure}")
        return 1

    print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE=pass")
    print(f"PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_CHECKED={checked}")
    return 0


def write_manifest(root: Path, survey_summary: dict[str, bool | str]) -> None:
    manifest_dir = root / "zigux/tests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "lane_key": "P12-L04",
        "phase": "Phase 12",
        "survey_summary": survey_summary,
    }
    (manifest_dir / "phase12_virtio_net_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def materialize_paths(root: Path, survey_summary: dict[str, bool | str]) -> None:
    for field, rel_path in REQUIRED_PRESENCE_FLAGS.items():
        path = root / rel_path
        if survey_summary.get(field) is True:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// fixture\n", encoding="utf-8")
        elif path.exists():
            path.unlink()


def build_current_like_summary() -> dict[str, bool]:
    return {
        "preexisting_phase10_build_present": True,
        "preexisting_virtio_core_zig_present": True,
        "preexisting_virtio_ring_zig_present": True,
        "preexisting_virtio_input_zig_present": True,
        "preexisting_phase12_build_present": True,
        "preexisting_phase12_virtio_net_survey_present": True,
        "preexisting_phase12_survey_note_present": True,
        "preexisting_virtio_net_queue_resume_zig_present": True,
        "preexisting_virtio_net_receive_refill_replay_zig_present": True,
        "preexisting_virtio_net_transmit_recycle_zig_present": True,
        "preexisting_virtio_net_post_reset_replay_zig_present": True,
        "preexisting_virtio_net_throughput_parity_zig_present": True,
        "preexisting_phase12_virtio_net_queue_resume_present": True,
        "preexisting_phase12_virtio_net_receive_refill_replay_present": True,
        "preexisting_phase12_virtio_net_transmit_recycle_present": True,
        "preexisting_phase12_virtio_net_post_reset_replay_present": True,
        "preexisting_phase12_virtio_net_throughput_parity_present": True,
        "preexisting_virtio_net_zig_present": False,
        "preexisting_phase12_virtio_net_zig_present": False,
        "preexisting_phase12_virtio_net_syntax_lab_present": True,
        "preexisting_phase12_virtio_net_syntax_lab_build_present": True,
    }


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12_virtio_net_manifest_presence_") as tmp:
        root = Path(tmp)

        current_like_summary = build_current_like_summary()
        write_manifest(root, current_like_summary)
        materialize_paths(root, current_like_summary)
        failures, checked = check_manifest_presence(root)
        assert checked == len(REQUIRED_PRESENCE_FLAGS)
        assert not failures, failures
        cases += 1

        missing_path = root / "zigux/tests/phase12_virtio_net_syntax_lab_build.zig"
        missing_path.unlink()
        failures, _ = check_manifest_presence(root)
        assert any("preexisting_phase12_virtio_net_syntax_lab_build_present" in failure for failure in failures), failures
        cases += 1

        invalid_summary = dict(current_like_summary)
        invalid_summary["preexisting_phase12_survey_note_present"] = "yes"
        write_manifest(root, invalid_summary)
        materialize_paths(root, current_like_summary)
        failures, _ = check_manifest_presence(root)
        assert any("expected boolean field" in failure for failure in failures), failures
        cases += 1

    print("PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_MANIFEST_PRESENCE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Phase 12 virtio_net manifest presence flags against current-tree files."
    )
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_live_check(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
