#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


FILES = {
    "guide": "Documentation/zigux/phase5-sample-review-guide.md",
    "kfifo": "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "kobject": "Documentation/zigux/phase5-kobject-sample-survey.md",
    "kretprobe": "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "trace_events": "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples_root": "samples/zigux/README.md",
}

REQUIRED_MARKERS = {
    "guide": [
        "# Phase 5 Sample Review Guide",
        "* the bytestream packet through `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig`",
        "* the kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`",
        "* the trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`",
        "* the kretprobe anchor through `Documentation/zigux/phase5-kretprobe-sample-survey.md` only",
        "Direct readback in this run did not recover these older Phase 5 packet paths:",
        "* `samples/zigux/kretprobe_example.zig`",
        "* `zigux/tests/phase5_build.zig`",
    ],
    "kfifo": [
        "# Phase 5 Kfifo Sample Survey",
        "`samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.",
        "- `zigux/tests/phase5_bytestream_fifo.zig`",
        "- `zigux/tests/phase5_bytestream_fifo_manifest.json`",
        "- `zigux/tests/phase5_bytestream_fifo_survey.zig`",
        "- `zigux/tests/phase5_build.zig`",
        "Treat those four paths as current public-tree gaps for this anchor until a fresh reread proves they returned.",
    ],
    "kobject": [
        "# Phase 5 Kobject Sample Survey",
        "- `samples/zigux/kobject_example.zig`",
        "- `zigux/tests/phase5_kobject_example.zig`",
        "- `zigux/tests/phase5_kobject_example_manifest.json`",
        "while `zigux/tests/phase5_kobject_example_survey.zig` and the shared `zigux/tests/phase5_build.zig` route are current public-tree gaps again.",
        "shared contributor guidance should keep the narrower packet explicit instead of presenting those missing paths as current evidence.",
    ],
    "kretprobe": [
        "# Phase 5 Kretprobe Sample Survey",
        "- `samples/zigux/kretprobe_example.zig`",
        "- `zigux/tests/phase5_build.zig`",
        "- `zigux/tests/phase5_kretprobe_example.zig`",
        "- `zigux/tests/phase5_kretprobe_example_manifest.json`",
        "- `zigux/tests/phase5_kretprobe_example_survey.zig`",
        "`Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still overstate that missing packet",
    ],
    "trace_events": [
        "# Phase 5 Trace-Events Sample Survey",
        "- `samples/zigux/trace_events_sample.zig`",
        "- `zigux/tests/phase5_trace_events_sample.zig`",
        "- `zigux/tests/phase5_trace_events_sample_manifest.json`",
        "- `zigux/tests/phase5_trace_events_sample_survey.zig`",
        "- `zigux/tests/phase5_build.zig`",
        "Treat the trace-events packet as directly readable through the sample root, focused replay, manifest, and survey replay above, while keeping the missing shared build entrypoint explicit until a fresh reread proves it returned.",
    ],
    "samples_root": [
        "# samples/zigux",
        "* `samples/zigux/bytestream_fifo.zig`",
        "* `samples/zigux/kobject_example.zig`",
        "* `samples/zigux/trace_events_sample.zig`",
        "But fresh direct readback in this run still did not recover `samples/zigux/kretprobe_example.zig` or the shared `zigux/tests/phase5_build.zig` route.",
    ],
}

FORBIDDEN_MARKERS = {
    "guide": [
        "* the kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`",
    ],
    "samples_root": [
        "Fresh repo-first inspection on 2026-05-13 directly recovered these approved non-runtime Phase 5 sample-root files from current `master`:\n\n* `samples/zigux/bytestream_fifo.zig`\n* `samples/zigux/kobject_example.zig`\n* `samples/zigux/kretprobe_example.zig`\n* `samples/zigux/trace_events_sample.zig`",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str) -> None:
    for marker in REQUIRED_MARKERS[label]:
        if marker not in text:
            raise CheckError(f"missing marker in {FILES[label]}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {FILES[label]}: {marker}")


def run_check(root: Path) -> None:
    for label in FILES:
        text = read_text(root, FILES[label])
        expect_markers(label, text)
        expect_forbidden_markers_absent(label, text)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    for label, relative_path in FILES.items():
        write_text(root / relative_path, "\n".join(REQUIRED_MARKERS[label]) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase5_survey_readback_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        cases: list[tuple[str, str]] = []
        for label, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                cases.append((label, marker))

        for idx, (label, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            (
                "guide",
                FORBIDDEN_MARKERS["guide"][0],
            ),
            (
                "samples_root",
                FORBIDDEN_MARKERS["samples_root"][0],
            ),
        ]

        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        total_case_count = len(cases) + len(forbidden_cases)
        print("PHASE5_SURVEY_READBACK_SELF_TEST=pass")
        print(f"PHASE5_SURVEY_READBACK_SELF_TEST_CASE_COUNT={total_case_count}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE5_SURVEY_READBACK=fail: {exc}")
        return 1

    print("PHASE5_SURVEY_READBACK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())