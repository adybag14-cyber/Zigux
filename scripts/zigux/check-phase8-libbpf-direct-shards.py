#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 2:
        return resolved.parents[1]
    return resolved.parent


ROOT = _default_root()

SURVEY_PATH = Path("Documentation/zigux/phase8-libbpf-segment-survey.md")
MAKEFILE_PATH = Path("zigux/Makefile")

DIRECT_HELPER_FILES = (
    Path("tools/lib/bpf/zigux_segments/verify.zig"),
    Path("tools/lib/bpf/zigux_segments/cpu_mask.zig"),
    Path("tools/lib/bpf/zigux_segments/logging.zig"),
    Path("tools/lib/bpf/zigux_segments/type_names.zig"),
    Path("tools/lib/bpf/zigux_segments/pin_path.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
)

REMINDER_FILES = (
    Path("Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
    Path("scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
    Path("zigux/tests/phase8_libbpf_segments_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll_only_build.zig"),
)

REQUIRED_FILES = (
    SURVEY_PATH,
    MAKEFILE_PATH,
    *DIRECT_HELPER_FILES,
    *REMINDER_FILES,
)

SURVEY_MARKERS = (
    "tools/lib/bpf/zigux_segments/verify.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/Makefile` Phase 8 route family are current exact-readable evidence",
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the bounded `make -C zigux phase8-perf-buffer-poll-test` route already keep the timing-adjacent no-timer and no-clockevent boundary explicit without claiming broader timeout-sensitive routing behavior",
)

MAKEFILE_MARKERS = (
    "phase8-libbpf-segments-test:",
    "phase8-perf-buffer-poll-test:",
)


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_root(root: Path) -> ValidationResult:
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    missing_markers: list[str] = []

    if (root / SURVEY_PATH).exists():
        survey = _read(root / SURVEY_PATH)
        for marker in SURVEY_MARKERS:
            if marker not in survey:
                missing_markers.append(f"{SURVEY_PATH}:{marker}")

    if (root / MAKEFILE_PATH).exists():
        makefile = _read(root / MAKEFILE_PATH)
        for marker in MAKEFILE_MARKERS:
            if marker not in makefile:
                missing_markers.append(f"{MAKEFILE_PATH}:{marker}")

    return ValidationResult(missing_files=missing_files, missing_markers=missing_markers)


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers:
        print("PHASE8_LIBBPF_DIRECT_SHARDS=fail")
        if result.missing_files:
            print("PHASE8_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_MISSING_MARKERS_END")
        return 1

    print("PHASE8_LIBBPF_DIRECT_SHARDS=pass")
    print(f"PHASE8_DIRECT_HELPER_COUNT={len(DIRECT_HELPER_FILES)}")
    print(f"PHASE8_REMINDER_FILE_COUNT={len(REMINDER_FILES)}")
    print(f"PHASE8_MARKER_COUNT={len(SURVEY_MARKERS) + len(MAKEFILE_MARKERS)}")
    return 0


def _passing_fixture(root: Path) -> None:
    _write(
        root / SURVEY_PATH,
        "\n".join(
            (
                "tools/lib/bpf/zigux_segments/verify.zig",
                "tools/lib/bpf/zigux_segments/cpu_mask.zig",
                "tools/lib/bpf/zigux_segments/logging.zig",
                "tools/lib/bpf/zigux_segments/type_names.zig",
                "tools/lib/bpf/zigux_segments/pin_path.zig",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "zigux/Makefile` Phase 8 route family are current exact-readable evidence",
                "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the bounded `make -C zigux phase8-perf-buffer-poll-test` route already keep the timing-adjacent no-timer and no-clockevent boundary explicit without claiming broader timeout-sensitive routing behavior",
            )
        ),
    )
    _write(
        root / MAKEFILE_PATH,
        "\n".join(
            (
                "phase8-libbpf-segments-test:",
                "phase8-perf-buffer-poll-test:",
            )
        ),
    )
    for path in DIRECT_HELPER_FILES:
        _write(root / path, "helper shard\n")
    for path in REMINDER_FILES:
        _write(root / path, "reminder shard\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-direct-shards-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        missing_helper = root / DIRECT_HELPER_FILES[0]
        missing_helper.unlink()
        helper_failure = validate_root(root)
        if DIRECT_HELPER_FILES[0].as_posix() not in helper_failure.missing_files:
            raise AssertionError("expected missing helper shard to be reported")
        _write(missing_helper, "helper shard\n")

        survey_path = root / SURVEY_PATH
        original_survey = _read(survey_path)
        survey_path.write_text(
            original_survey.replace("tools/lib/bpf/zigux_segments/logging.zig", "", 1),
            encoding="utf-8",
        )
        survey_failure = validate_root(root)
        expected_survey_marker = f"{SURVEY_PATH}:tools/lib/bpf/zigux_segments/logging.zig"
        if expected_survey_marker not in survey_failure.missing_markers:
            raise AssertionError("expected missing direct-helper survey marker to be reported")
        survey_path.write_text(original_survey, encoding="utf-8")

        makefile_path = root / MAKEFILE_PATH
        original_makefile = _read(makefile_path)
        makefile_path.write_text(
            original_makefile.replace("phase8-perf-buffer-poll-test:", "", 1),
            encoding="utf-8",
        )
        makefile_failure = validate_root(root)
        expected_makefile_marker = f"{MAKEFILE_PATH}:phase8-perf-buffer-poll-test:"
        if expected_makefile_marker not in makefile_failure.missing_markers:
            raise AssertionError("expected missing make route marker to be reported")
        makefile_path.write_text(original_makefile, encoding="utf-8")

    print("PHASE8_LIBBPF_DIRECT_SHARDS_SELFTEST=pass")
    print("PHASE8_LIBBPF_DIRECT_SHARDS_SELFTEST_CASE_COUNT=4")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
