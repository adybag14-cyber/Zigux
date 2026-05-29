#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

INPUT_SHARD_MARKERS = [
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-closure-evidence.md": [
        "# Phase 10 Closure Evidence",
        "input lane's helper-local packet stays reviewable",
        "phase10-virtio-input-registration-lifecycle",
        *INPUT_SHARD_MARKERS,
    ],
    "Documentation/zigux/phase10-virtio-input-survey.md": [
        "# Phase 10 Virtio Input Survey",
        "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport",
        "Current `master` keeps this input lane reviewable through the bounded helper packet:",
        "phase10-virtio-input-registration-lifecycle",
        *INPUT_SHARD_MARKERS,
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "# Phase 10, 11, and 13 Tests-Root Review Companion",
        "directly re-readable input packet anchors",
        "returned shared closure packet anchors",
        "scripts/zigux/check-phase10-input-packet.py",
        *INPUT_SHARD_MARKERS,
    ],
}


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            missing_files.append(relative_path)
            continue

        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                missing_markers.append(f"{relative_path}:{marker}")

    return missing_files, missing_markers


def required_marker_count() -> int:
    return sum(len(markers) for markers in REQUIRED_MARKERS.values())


def write_fixture(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_fixture(root)
        missing_files, missing_markers = validate(root)
        assert missing_files == []
        assert missing_markers == []

        closure_note = root / "Documentation/zigux/phase10-closure-evidence.md"
        closure_note.write_text(
            closure_note.read_text(encoding="utf-8").replace(
                "input lane's helper-local packet stays reviewable\n",
                "",
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        assert "Documentation/zigux/phase10-closure-evidence.md:input lane's helper-local packet stays reviewable" in missing_markers

        write_fixture(root)
        survey_note = root / "Documentation/zigux/phase10-virtio-input-survey.md"
        survey_note.write_text(
            survey_note.read_text(encoding="utf-8").replace(
                "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport\n",
                "",
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        assert "Documentation/zigux/phase10-virtio-input-survey.md:PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport" in missing_markers

        write_fixture(root)
        tests_root = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        tests_root.write_text(
            tests_root.read_text(encoding="utf-8").replace(
                "directly re-readable input packet anchors\n",
                "",
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        assert "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:directly re-readable input packet anchors" in missing_markers

        write_fixture(root)
        helper_marker_path = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        helper_marker_path.write_text(
            helper_marker_path.read_text(encoding="utf-8").replace(
                "drivers/virtio/virtio_input_teardown_observation.zig\n",
                "",
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        assert "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:drivers/virtio/virtio_input_teardown_observation.zig" in missing_markers

    print("PHASE10_INPUT_SHARED_REMINDER_EVIDENCE_SELF_TEST=pass")
    print("PHASE10_INPUT_SHARED_REMINDER_EVIDENCE_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 10 input reminder surfaces keep helper-shard evidence explicit.")
    parser.add_argument("--self-test", action="store_true", help="run synthetic drift tests for this checker")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_INPUT_SHARED_REMINDER_EVIDENCE=fail")
        print("MISSING_PHASE10_INPUT_SHARED_REMINDER_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_SHARED_REMINDER_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_SHARED_REMINDER_EVIDENCE=fail")
        print("MISSING_PHASE10_INPUT_SHARED_REMINDER_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_SHARED_REMINDER_MARKERS_END")
        return 1

    print("PHASE10_INPUT_SHARED_REMINDER_EVIDENCE=pass")
    print(f"PHASE10_INPUT_SHARED_REMINDER_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE10_INPUT_SHARED_REMINDER_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
