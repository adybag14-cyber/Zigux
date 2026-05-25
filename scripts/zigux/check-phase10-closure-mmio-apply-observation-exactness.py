#!/usr/bin/env python3
"""Fail closed when Phase 10 closure evidence and its validator drift on the MMIO apply-observation replay."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
VALIDATOR_PATH = "scripts/zigux/validate-phase10-closure.py"

MMIO_REPLAY_PATH = "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig"
MMIO_REPLAY_LABEL = "phase10 mmio apply-observation replay"

MANIFEST_TEST_MARKER = f'"{MMIO_REPLAY_PATH}"'
MANIFEST_REPLAY_MARKER = f'"{MMIO_REPLAY_PATH}": ['
MANIFEST_LABEL_MARKER = f'"{MMIO_REPLAY_LABEL}"'

VALIDATOR_TEST_MARKER = f'    "{MMIO_REPLAY_PATH}",'
VALIDATOR_REPLAY_MARKER = f'    "{MMIO_REPLAY_PATH}",'


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing(root: Path) -> list[str]:
    missing: list[str] = []
    manifest_text = read_text(root, MANIFEST_PATH)
    validator_text = read_text(root, VALIDATOR_PATH)
    manifest_tests_block = _extract_manifest_tests_block(manifest_text)
    manifest_replays_block = _extract_manifest_replays_block(manifest_text)

    if MANIFEST_TEST_MARKER not in manifest_tests_block:
        missing.append(f"manifest_tests:{MMIO_REPLAY_PATH}")
    if MANIFEST_REPLAY_MARKER not in manifest_replays_block:
        missing.append(f"manifest_focused_harness_replays:{MMIO_REPLAY_PATH}")
    if MANIFEST_LABEL_MARKER not in manifest_replays_block:
        missing.append(f"manifest_focused_harness_label:{MMIO_REPLAY_LABEL}")

    expected_tests_block = _extract_list_block(validator_text, "EXPECTED_TESTS = [")
    if VALIDATOR_TEST_MARKER not in expected_tests_block:
        missing.append(f"validator_expected_tests:{MMIO_REPLAY_PATH}")

    focused_replays_block = _extract_list_block(validator_text, "FOCUSED_HARNESS_REPLAY_FILES = [")
    if VALIDATOR_REPLAY_MARKER not in focused_replays_block:
        missing.append(f"validator_focused_harness_replays:{MMIO_REPLAY_PATH}")

    return missing


def _extract_list_block(text: str, anchor: str) -> str:
    start = text.find(anchor)
    if start == -1:
        return ""
    end = text.find("\n]\n", start)
    if end == -1:
        return text[start:]
    return text[start : end + 3]


def _extract_manifest_tests_block(text: str) -> str:
    anchor = '"tests": ['
    start = text.find(anchor)
    if start == -1:
        return ""
    end = text.find('\n  ],', start)
    if end == -1:
        return text[start:]
    return text[start : end + 5]


def _extract_manifest_replays_block(text: str) -> str:
    anchor = '"focused_harness_replays": {'
    start = text.find(anchor)
    if start == -1:
        return ""
    end = text.find('\n  }', start)
    if end == -1:
        return text[start:]
    return text[start : end + 4]


def write_sample_root(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        "{\n"
        '  "test_count": 30,\n'
        '  "tests": [\n'
        '    "zigux/tests/phase10_virtio_mmio.zig",\n'
        f'    "{MMIO_REPLAY_PATH}",\n'
        '    "drivers/virtio/virtio_mmio_verify.zig",\n'
        '    "zigux/tests/phase10_virtio_mmio_survey.zig",\n'
        '    "zigux/tests/phase10_build.zig"\n'
        "  ],\n"
        '  "focused_harness_replays": {\n'
        f'    "{MMIO_REPLAY_PATH}": [\n'
        f'      "{MMIO_REPLAY_LABEL}"\n'
        "    ]\n"
        "  }\n"
        "}\n",
    )
    write_text(
        root / VALIDATOR_PATH,
        "FOCUSED_HARNESS_REPLAY_FILES = [\n"
        f'    "{MMIO_REPLAY_PATH}",\n'
        "]\n\n"
        "EXPECTED_TESTS = [\n"
        f'    "{MMIO_REPLAY_PATH}",\n'
        "]\n",
    )


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase10_mmio_apply_exactness_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        baseline = collect_missing(root)
        if baseline:
            actual = ",".join(baseline)
            raise SystemExit(f"phase10-mmio-apply-self-test:baseline_failed:{actual}")
        cases += 1

        manifest_path = root / MANIFEST_PATH
        validator_path = root / VALIDATOR_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        original_validator = validator_path.read_text(encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(f'    "{MMIO_REPLAY_PATH}",\n', "", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing(root),
            f"manifest_tests:{MMIO_REPLAY_PATH}",
            "phase10-mmio-apply-self-test",
        )
        cases += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(f'    "{MMIO_REPLAY_PATH}": [\n', "", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing(root),
            f"manifest_focused_harness_replays:{MMIO_REPLAY_PATH}",
            "phase10-mmio-apply-self-test",
        )
        cases += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(f'      "{MMIO_REPLAY_LABEL}"\n', '      "wrong label"\n', 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing(root),
            f"manifest_focused_harness_label:{MMIO_REPLAY_LABEL}",
            "phase10-mmio-apply-self-test",
        )
        cases += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(f'    "{MMIO_REPLAY_PATH}",\n', "", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing(root),
            f"validator_focused_harness_replays:{MMIO_REPLAY_PATH}",
            "phase10-mmio-apply-self-test",
        )
        cases += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(
                "EXPECTED_TESTS = [\n"
                f'    "{MMIO_REPLAY_PATH}",\n'
                "]\n",
                "EXPECTED_TESTS = [\n]\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing(root),
            f"validator_expected_tests:{MMIO_REPLAY_PATH}",
            "phase10-mmio-apply-self-test",
        )
        cases += 1

    print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when Phase 10 closure evidence and its validator diverge on the MMIO apply-observation replay."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    missing = collect_missing(args.root)
    if missing:
        print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS=fail")
        print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS_MISSING_END")
        return 1

    print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_EXACTNESS=pass")
    print("PHASE10_CLOSURE_MMIO_APPLY_OBSERVATION_REPLAY_PATH=zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
