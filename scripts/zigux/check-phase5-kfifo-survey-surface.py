#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase5-kfifo-sample-survey.md")

REQUIRED_MARKERS = (
    "This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.",
    "- `PHASE5_LANE_KEY=P5-L01`",
    "- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.",
    "- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.",
    "- the shipped sample-root companion `samples/zigux/bytestream_fifo_window_contract.zig` is directly readable on current `master`",
    "- the broader exact behavior packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`",
    "- the manifest-backed packet remains directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`.",
    "- the survey packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`",
    "- authenticated GitHub contents reads in this environment now recover `zigux/tests/phase5_build.zig` directly again",
    "- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`",
    "- keep remaining-capacity, rollover, occupancy, queue-shape, and two-window contract cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, `usesWrappedStorageWindow()`, and `samples/zigux/bytestream_fifo_window_contract.zig`",
    "- keep the direct `available()` helper explicit as the first remaining-capacity cue at cold, initialized, preview, wrapped, full, replay-complete, reset, and exited boundaries instead of leaving free-space review to derived queue-length math alone",
    "- keep bitmap helper or runtime bitmap claims out of this packet; current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample",
    "- `samples/zigux/bytestream_fifo.zig` currently carries four in-file self-checks",
    "- `samples/zigux/bytestream_fifo_window_contract.zig` currently carries two direct companion checks",
    "- `zigux/tests/phase5_bytestream_fifo.zig` currently carries five focused replay tests",
    "- `zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries five survey-packet checks",
    "- `zigux/tests/phase5_build.zig` is directly readable through authenticated contents readback again and now reruns the sample-owned self-check route, the window-contract companion, the focused replay packet, and the survey gate together",
    "- `StorageBacking.embedded_fixed_buffer` is the only declared storage backing",
    "- does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c`, keep `requires_runtime_substrate = false`, keep `provides_selfcheck = true`, and keep `StorageBacking.embedded_fixed_buffer` as the only storage backing so the packet stays in the non-runtime Phase 5 lane?",
    "- do `runAnchorReplay()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `runRemainingCapacityReplay()`, `runPartialEnqueueBoundaryReplay()`, `runReinitBoundaryReplay()`, and `samples/zigux/bytestream_fifo_window_contract.zig` still describe the same bounded packet across the sample root, focused replay file, manifest-backed contract, dedicated survey gate, and shared reminder surfaces?",
    "- do the direct validation routes stay explicit too: `zig test samples/zigux/bytestream_fifo.zig` should stay visible as the sample-owned self-check route, `zig test samples/zigux/bytestream_fifo_window_contract.zig` should stay visible as the queue-window companion route, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig` should stay visible as the equivalent direct focused replay route, `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` should stay visible as the survey-packet guard, and the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` line should stay visible as the current direct shared build route that reruns the sample-owned self-check route, the window-contract companion, the focused replay packet, and the survey guard together rather than being demoted back to companion-only wording?",
)

REQUIRED_PATHS = (
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "samples/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/bytestream_fifo_window_contract.zig",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_build.zig",
)

FORBIDDEN_MARKERS = (
    "current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so this bytestream packet must not be used to imply bitmap-side sample delivery or reopen the separate later-phase runtime bitmap family",
    "write a new sample",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder(rel: str) -> str:
    return f"present: {rel}\n"


def survey_fixture() -> str:
    lines = ["# Phase 5 Kfifo Sample Survey", ""]
    lines.extend(REQUIRED_MARKERS)
    lines.append("")
    lines.extend(f"`{rel}`" for rel in REQUIRED_PATHS)
    lines.append("")
    return "\n".join(lines) + "\n"


def seed(root: Path) -> None:
    write_text(root, SURVEY_PATH, survey_fixture())
    for rel in REQUIRED_PATHS:
        rel_path = Path(rel)
        if rel_path == SURVEY_PATH:
            continue
        write_text(root, rel_path, placeholder(rel))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    survey = read_text(root, SURVEY_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in survey:
            failures.append(f"missing_text:{marker}")
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_path:{rel}")
        if rel != str(SURVEY_PATH) and f"`{rel}`" not in survey and rel not in survey:
            failures.append(f"missing_reference:{rel}")
    for forbidden in FORBIDDEN_MARKERS:
        if forbidden in survey:
            failures.append(f"forbidden_text:{forbidden}")
    return failures


def run_self_test() -> int:
    cases_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_kfifo_survey_surface_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        assert collect_failures(root) == []
        cases_run += 1

        mutated = root / "missing_marker"
        seed(mutated)
        text = read_text(mutated, SURVEY_PATH).replace(REQUIRED_MARKERS[4], "", 1)
        write_text(mutated, SURVEY_PATH, text)
        assert collect_failures(mutated) == [f"missing_text:{REQUIRED_MARKERS[4]}"]
        cases_run += 1

        mutated = root / "missing_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_build.zig").unlink()
        assert collect_failures(mutated) == ["missing_path:zigux/tests/phase5_build.zig"]
        cases_run += 1

        mutated = root / "forbidden_old_gap_wording"
        seed(mutated)
        write_text(mutated, SURVEY_PATH, read_text(mutated, SURVEY_PATH) + FORBIDDEN_MARKERS[0] + "\n")
        assert collect_failures(mutated) == [f"forbidden_text:{FORBIDDEN_MARKERS[0]}"]
        cases_run += 1

        mutated = root / "forbidden_new_sample_wording"
        seed(mutated)
        write_text(mutated, SURVEY_PATH, read_text(mutated, SURVEY_PATH) + FORBIDDEN_MARKERS[1] + "\n")
        assert collect_failures(mutated) == [f"forbidden_text:{FORBIDDEN_MARKERS[1]}"]
        cases_run += 1

        mutated = root / "missing_anchor_marker"
        seed(mutated)
        text = read_text(mutated, SURVEY_PATH).replace(REQUIRED_MARKERS[2], "", 1)
        write_text(mutated, SURVEY_PATH, text)
        assert collect_failures(mutated) == [f"missing_text:{REQUIRED_MARKERS[2]}"]
        cases_run += 1

        mutated = root / "missing_validation_marker"
        seed(mutated)
        text = read_text(mutated, SURVEY_PATH).replace(REQUIRED_MARKERS[-1], "", 1)
        write_text(mutated, SURVEY_PATH, text)
        assert collect_failures(mutated) == [f"missing_text:{REQUIRED_MARKERS[-1]}"]
        cases_run += 1

    if cases_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, got {cases_run}")
    print("PHASE5_KFIFO_SURVEY_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_KFIFO_SURVEY_SURFACE_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 5 kfifo survey drifts away from the roadmap-backed bytestream packet."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a packet-shaped sample root for manual replay and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        seed(args.write_sample_root)
        print(f"PHASE5_KFIFO_SURVEY_SURFACE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KFIFO_SURVEY_SURFACE=fail")
        for failure in failures:
            print(f"PHASE5_KFIFO_SURVEY_SURFACE_FAILURE={failure}")
        return 1

    print("PHASE5_KFIFO_SURVEY_SURFACE=pass")
    print(f"PHASE5_KFIFO_SURVEY_SURFACE_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE5_KFIFO_SURVEY_SURFACE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
