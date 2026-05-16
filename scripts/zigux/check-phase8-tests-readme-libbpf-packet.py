#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) >= 4 else SELF_PATH.parent
TESTS_README_PATH = ROOT / "zigux/tests/README.md"

REQUIRED_MARKERS = (
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    "`zigux/tests/phase8_cpu_mask.zig`",
    "`zigux/tests/phase8_logging.zig`",
    "`zigux/tests/phase8_pin_path.zig`",
    "`zigux/tests/phase8_bpf_type_names.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_libbpf_segments.zig`",
    "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
    "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
    "`make -C zigux phase8-cpu-mask-test`",
    "`make -C zigux phase8-file-path-handle-bridge-test`",
    "`make -C zigux phase8-libbpf-segments-test`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def check_tests_readme(path: Path) -> None:
    content = load_text(path)
    missing = [marker for marker in REQUIRED_MARKERS if marker not in content]
    if missing:
        raise SystemExit(
            "phase8 tests README libbpf packet drift:\n"
            + "\n".join(f"- missing marker: {marker}" for marker in missing)
        )


def run_self_test() -> None:
    sample = "\n".join(REQUIRED_MARKERS) + "\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        readme = root / "README.md"
        readme.write_text(sample, encoding="utf-8")
        check_tests_readme(readme)

        for marker in REQUIRED_MARKERS:
            readme.write_text(sample.replace(marker, "", 1), encoding="utf-8")
            try:
                check_tests_readme(readme)
            except SystemExit:
                pass
            else:
                raise SystemExit(f"self-test expected drift for marker: {marker}")
            readme.write_text(sample, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when zigux/tests/README.md drops the Phase 8 libbpf, "
            "perf-buffer, and shared route markers that current master advertises."
        )
    )
    parser.add_argument(
        "--tests-readme",
        type=Path,
        default=TESTS_README_PATH,
        help="override the tests README path for focused checks or self-tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in temporary-workspace regression test",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    check_tests_readme(args.tests_readme)


if __name__ == "__main__":
    main()
