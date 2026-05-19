#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README_PATH = Path("samples/zigux/README.md")

DIRECT_PROOF_PATHS = (
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
)

REQUIRED_TEXT = (
    "For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
    "Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly.",
    "Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.",
    "For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet.",
    "Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.",
    "Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.",
)

FORBIDDEN_TEXT = (
    "For the trace-events anchor, current `master` now keeps the direct non-runtime sample packet readable through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`",
    "Keep the direct sample, focused replay, manifest, and survey replay as the current direct packet proof",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = _read(root / README_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in readme:
            failures.append(f"readme:missing_text:{marker}")

    for marker in FORBIDDEN_TEXT:
        if marker in readme:
            failures.append(f"readme:forbidden_text:{marker}")

    for rel in DIRECT_PROOF_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"readme:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    return failures


def _sample_readme() -> str:
    return """# samples/zigux

This directory is the sample-root boundary for Zigux.

Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.
Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.
For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly.
Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.
For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet.
Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.
Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.
"""


def _seed(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    for rel in DIRECT_PROOF_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 4
    with tempfile.TemporaryDirectory(prefix="phase5_sample_root_trace_events_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_required_root = root / "missing_required"
        _seed(missing_required_root)
        _write(
            missing_required_root / README_PATH,
            _sample_readme().replace(REQUIRED_TEXT[1], "", 1),
        )
        failures = collect_failures(missing_required_root)
        expected = [f"readme:missing_text:{REQUIRED_TEXT[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-required failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(
            forbidden_text_root / README_PATH,
            _sample_readme() + "\n" + FORBIDDEN_TEXT[0] + "\n",
        )
        failures = collect_failures(forbidden_text_root)
        expected = [f"readme:forbidden_text:{FORBIDDEN_TEXT[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

        missing_direct_file_root = root / "missing_direct_file"
        _seed(missing_direct_file_root)
        (missing_direct_file_root / DIRECT_PROOF_PATHS[2]).unlink()
        failures = collect_failures(missing_direct_file_root)
        expected = [f"repo:missing_direct_path:{DIRECT_PROOF_PATHS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-file failure: {failures}")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 sample-root README keeps the trace-events boundary truthful."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY=pass")
    print(f"PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY_DIRECT_PROOF_COUNT={len(DIRECT_PROOF_PATHS)}")
    print(f"PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY_REQUIRED_TEXT_COUNT={len(REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
