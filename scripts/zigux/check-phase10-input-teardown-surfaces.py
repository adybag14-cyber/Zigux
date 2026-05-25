#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/check-phase10-input-packet.py",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_build.zig",
]

INPUT_SURVEY_MARKERS = [
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "the dedicated teardown-preflight helper and replay",
]

CLOSURE_NOTE_MARKERS = [
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "scripts/zigux/check-phase10-input-packet.py",
]

COMPANION_MARKERS = [
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
]

INPUT_CHECKER_MARKERS = [
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
]

BUILD_MARKERS = [
    "phase10_virtio_input_teardown_preflight_module",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
]

EVIDENCE_DRIVER = "drivers/virtio/virtio_input_teardown_preflight.zig"
EVIDENCE_REPLAY = "zigux/tests/phase10_virtio_input_teardown_preflight.zig"


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for rel_path in FILES:
        if not (root / rel_path).is_file():
            missing_files.append(rel_path)

    if missing_files:
        return missing_files, missing_markers

    check_markers(
        missing_markers,
        "input_survey",
        read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"),
        INPUT_SURVEY_MARKERS,
    )
    check_markers(
        missing_markers,
        "closure_note",
        read_text(root, "Documentation/zigux/phase10-closure-evidence.md"),
        CLOSURE_NOTE_MARKERS,
    )
    check_markers(
        missing_markers,
        "tests_root_companion",
        read_text(root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"),
        COMPANION_MARKERS,
    )
    check_markers(
        missing_markers,
        "input_checker",
        read_text(root, "scripts/zigux/check-phase10-input-packet.py"),
        INPUT_CHECKER_MARKERS,
    )
    check_markers(
        missing_markers,
        "phase10_build",
        read_text(root, "zigux/tests/phase10_build.zig"),
        BUILD_MARKERS,
    )

    closure_manifest = read_json(root, "zigux/tests/phase10_closure_manifest.json")
    evidence = (
        closure_manifest.get("roadmap_parity_scoreboard", {})
        .get("lab_only_driver_validation", {})
        .get("evidence", [])
    )
    if EVIDENCE_DRIVER not in evidence:
        missing_markers.append(f"closure_manifest:evidence:{EVIDENCE_DRIVER}")
    if EVIDENCE_REPLAY not in evidence:
        missing_markers.append(f"closure_manifest:evidence:{EVIDENCE_REPLAY}")

    focused_harness = closure_manifest.get("focused_harness_replays", {})
    if EVIDENCE_REPLAY not in focused_harness:
        missing_markers.append(f"closure_manifest:focused_harness_replays:{EVIDENCE_REPLAY}")

    tests = closure_manifest.get("tests", [])
    if EVIDENCE_REPLAY not in tests:
        missing_markers.append(f"closure_manifest:tests:{EVIDENCE_REPLAY}")

    return missing_files, missing_markers


def write_fixture(root: Path) -> None:
    fixture_text = {
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(INPUT_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(COMPANION_MARKERS) + "\n",
        "scripts/zigux/check-phase10-input-packet.py": "\n".join(INPUT_CHECKER_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    }
    for rel_path, content in fixture_text.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    closure_manifest = {
        "roadmap_parity_scoreboard": {
            "lab_only_driver_validation": {
                "evidence": [EVIDENCE_DRIVER, EVIDENCE_REPLAY],
            }
        },
        "focused_harness_replays": {
            EVIDENCE_REPLAY: ["phase10 input teardown-preflight replay"],
        },
        "tests": [EVIDENCE_REPLAY],
    }
    manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(manifest_path, closure_manifest)


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


def expect_json_missing(root: Path, mutate, expected: str) -> None:
    path = root / "zigux/tests/phase10_closure_manifest.json"
    original = read_json(root, "zigux/tests/phase10_closure_manifest.json")
    mutated = mutate(json.loads(json.dumps(original)))
    write_json(path, mutated)
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"expected={expected}:actual={actual}")
    write_json(path, original)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_teardown_") as tmp_dir:
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
                "Documentation/zigux/phase10-virtio-input-survey.md",
                EVIDENCE_REPLAY,
                "zigux/tests/phase10_virtio_input_teardown_preflight_missing.zig",
                f"input_survey:{EVIDENCE_REPLAY}",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                EVIDENCE_DRIVER,
                "drivers/virtio/virtio_input_teardown_preflight_missing.zig",
                f"closure_note:{EVIDENCE_DRIVER}",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                EVIDENCE_REPLAY,
                "zigux/tests/phase10_virtio_input_teardown_preflight_missing.zig",
                f"tests_root_companion:{EVIDENCE_REPLAY}",
            ),
            (
                "scripts/zigux/check-phase10-input-packet.py",
                "\"phase10-virtio-input-teardown-preflight-tests\"",
                "\"phase10-virtio-input-teardown-preflight-drift\"",
                "input_checker:\"phase10-virtio-input-teardown-preflight-tests\"",
            ),
            (
                "zigux/tests/phase10_build.zig",
                "phase10_virtio_input_teardown_preflight_module",
                "phase10_virtio_input_teardown_preflight_missing_module",
                "phase10_build:phase10_virtio_input_teardown_preflight_module",
            ),
        ]
        for rel_path, old, new, expected in text_cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        expect_json_missing(
            root,
            lambda data: {
                **data,
                "roadmap_parity_scoreboard": {
                    "lab_only_driver_validation": {
                        "evidence": [EVIDENCE_REPLAY],
                    }
                },
            },
            f"closure_manifest:evidence:{EVIDENCE_DRIVER}",
        )
        expect_json_missing(
            root,
            lambda data: {
                **data,
                "focused_harness_replays": {},
            },
            f"closure_manifest:focused_harness_replays:{EVIDENCE_REPLAY}",
        )
        expect_json_missing(
            root,
            lambda data: {
                **data,
                "tests": [],
            },
            f"closure_manifest:tests:{EVIDENCE_REPLAY}",
        )

    print("PHASE10_INPUT_TEARDOWN_SURFACES_SELF_TEST=pass")
    print("PHASE10_INPUT_TEARDOWN_SURFACES_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the landed Phase 10 teardown-preflight evidence across the shared virtio lab reminder packet."
    )
    parser.add_argument("--self-test", action="store_true", help="run the synthetic drift checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_INPUT_TEARDOWN_SURFACES=fail")
        print("MISSING_PHASE10_INPUT_TEARDOWN_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_TEARDOWN_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_TEARDOWN_SURFACES=fail")
        print("MISSING_PHASE10_INPUT_TEARDOWN_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_TEARDOWN_MARKERS_END")
        return 1

    print("PHASE10_INPUT_TEARDOWN_SURFACES=pass")
    print(f"PHASE10_INPUT_TEARDOWN_REQUIRED_FILE_COUNT={len(FILES)}")
    print("PHASE10_INPUT_TEARDOWN_REQUIRED_EVIDENCE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
