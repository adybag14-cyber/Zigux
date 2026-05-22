#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "Documentation/zigux/phase10-virtio-input-survey.md",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "drivers/virtio/virtio_input_status_drain.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    ),
    "Documentation/zigux/review-checklist.md": (
        "scripts/zigux/check-phase10-input-packet.py",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "drivers/virtio/virtio_input_status_drain.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    ),
    "Documentation/zigux/phase10-closure-evidence.md": (
        "scripts/zigux/check-phase10-input-packet.py",
        "drivers/virtio/virtio_input_verify.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    ),
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": (
        "Documentation/zigux/phase10-virtio-input-survey.md",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "drivers/virtio/virtio_input_status_drain.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "Keep the input-lane helper names `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, and `drivers/virtio/virtio_input_teardown_observation.zig` explicit",
    ),
    "scripts/zigux/README.md": (
        "Documentation/zigux/phase10-virtio-input-survey.md",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
        "drivers/virtio/virtio_input_status_drain.zig",
        "drivers/virtio/virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")
    return [], missing_markers


def required_marker_count() -> int:
    return sum(len(markers) for markers in MARKERS.values())


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture(root: Path) -> None:
    for rel_path, markers in MARKERS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.unlink()
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"unexpected_missing_markers:{','.join(missing_markers)}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"expected={rel_path}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_review_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        text_cases = [
            (
                "Documentation/zigux/README.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_missing.zig",
                "Documentation/zigux/README.md:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/review-checklist.md",
                "zigux/tests/phase10_virtio_input_status_drain.zig",
                "zigux/tests/phase10_virtio_input_status_drain_missing.zig",
                "Documentation/zigux/review-checklist.md:zigux/tests/phase10_virtio_input_status_drain.zig",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "zigux/tests/phase10_virtio_input_teardown_observation.zig",
                "zigux/tests/phase10_virtio_input_teardown_missing.zig",
                "Documentation/zigux/phase10-closure-evidence.md:zigux/tests/phase10_virtio_input_teardown_observation.zig",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "zigux/tests/phase10_virtio_input_teardown_observation.zig",
                "zigux/tests/phase10_virtio_input_teardown_missing.zig",
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:zigux/tests/phase10_virtio_input_teardown_observation.zig",
            ),
            (
                "scripts/zigux/README.md",
                "zigux/tests/phase10_virtio_input_teardown_observation.zig",
                "zigux/tests/phase10_virtio_input_teardown_missing.zig",
                "scripts/zigux/README.md:zigux/tests/phase10_virtio_input_teardown_observation.zig",
            ),
        ]
        for rel_path, old, new, expected in text_cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        expect_missing_file(root, "Documentation/zigux/README.md")
        expect_missing_file(root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")

    print("PHASE10_INPUT_REVIEW_SURFACES_SELF_TEST=pass")
    print("PHASE10_INPUT_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the shared Phase 10 input reminder surfaces keep queue-callback, status-drain, and teardown packet anchors explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="run the checker's built-in synthetic drift tests")
    parser.add_argument("--root", help="repository root to validate")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT.resolve()
    missing_files, missing_markers = validate(root)
    if missing_files:
        print("PHASE10_INPUT_REVIEW_SURFACES=fail")
        print("MISSING_PHASE10_INPUT_REVIEW_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_REVIEW_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_REVIEW_SURFACES=fail")
        print("MISSING_PHASE10_INPUT_REVIEW_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_REVIEW_MARKERS_END")
        return 1

    print("PHASE10_INPUT_REVIEW_SURFACES=pass")
    print(f"PHASE10_INPUT_REVIEW_SURFACES_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE10_INPUT_REVIEW_SURFACES_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
