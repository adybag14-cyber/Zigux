#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REQUIRED_FILES = [
    "Documentation/zigux/phase5-sample-review-guide.md",
    "samples/zigux/README.md",
    "zigux/tests/README.md",
]

GUIDE_MARKERS = [
    "* `samples/kfifo/bytestream-example.c`",
    "* `samples/kobject/kobject-example.c`",
    "* `samples/kprobes/kretprobe_example.c`",
    "* `samples/trace_events/trace-events-sample.c`",
    "Repeated current-run GitHub-app contents reads for `scripts/zigux/README.md` still returned `Not Found`, so keep that older scripts-root reminder out of the current shared-surface inventory until a fresh reread proves the exact path returned again.",
    "Keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary",
]

SAMPLES_README_MARKERS = [
    "* `samples/zigux/bytestream_fifo.zig`",
    "* `samples/zigux/kobject_example.zig`",
    "* `samples/zigux/kretprobe_example.zig`",
    "* `samples/zigux/trace_events_sample.zig`",
    "Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.",
    "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample.",
    "current public-tree-backed companion evidence rather than direct authenticated-contents proof",
]

TESTS_README_MARKERS = [
    "* `Documentation/zigux/phase5-kfifo-sample-survey.md`",
    "* `zigux/tests/phase5_bytestream_fifo_manifest.json`",
    "* `Documentation/zigux/phase5-kobject-sample-survey.md`",
    "* `zigux/tests/phase5_kobject_example_manifest.json`",
    "* `Documentation/zigux/phase5-kretprobe-sample-survey.md`",
    "* `zigux/tests/phase5_kretprobe_example_manifest.json`",
    "* `Documentation/zigux/phase5-trace-events-sample-survey.md`",
    "* `zigux/tests/phase5_trace_events_sample_manifest.json`",
    "* current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
]


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_markers(text: str, prefix: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")
    return missing


def validate_root(root: Path) -> list[str]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return [f"missing_file:{path}" for path in missing_files]

    guide = read_text(root, "Documentation/zigux/phase5-sample-review-guide.md")
    samples_readme = read_text(root, "samples/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")

    missing_markers: list[str] = []
    missing_markers.extend(collect_missing_markers(guide, "guide", GUIDE_MARKERS))
    missing_markers.extend(
        collect_missing_markers(samples_readme, "samples_readme", SAMPLES_README_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(tests_readme, "tests_readme", TESTS_README_MARKERS)
    )
    return missing_markers


def write_fixture_tree(root: Path) -> None:
    fixture_text = {
        "Documentation/zigux/phase5-sample-review-guide.md": "\n".join(
            [
                "# Phase 5 Sample Review Guide",
                "",
                "## Roadmap anchors",
                "* `samples/kfifo/bytestream-example.c`",
                "* `samples/kobject/kobject-example.c`",
                "* `samples/kprobes/kretprobe_example.c`",
                "* `samples/trace_events/trace-events-sample.c`",
                "",
                "## Current repo reality on `master`",
                "Repeated current-run GitHub-app contents reads for `scripts/zigux/README.md` still returned `Not Found`, so keep that older scripts-root reminder out of the current shared-surface inventory until a fresh reread proves the exact path returned again.",
                "",
                "Keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary",
                "",
            ]
        ),
        "samples/zigux/README.md": "\n".join(
            [
                "# samples/zigux",
                "",
                "* `samples/zigux/bytestream_fifo.zig`",
                "* `samples/zigux/kobject_example.zig`",
                "* `samples/zigux/kretprobe_example.zig`",
                "* `samples/zigux/trace_events_sample.zig`",
                "",
                "Keep shared sample-root wording aligned with that mixed kobject packet: the survey note, sample, focused test, and manifest are directly readable here, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay current public-tree-backed companion evidence rather than direct authenticated-contents proof.",
                "",
                "Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.",
                "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample.",
                "",
            ]
        ),
        "zigux/tests/README.md": "\n".join(
            [
                "# zigux/tests",
                "",
                "* `Documentation/zigux/phase5-kfifo-sample-survey.md`",
                "* `zigux/tests/phase5_bytestream_fifo_manifest.json`",
                "* `Documentation/zigux/phase5-kobject-sample-survey.md`",
                "* `zigux/tests/phase5_kobject_example_manifest.json`",
                "* `Documentation/zigux/phase5-kretprobe-sample-survey.md`",
                "* `zigux/tests/phase5_kretprobe_example_manifest.json`",
                "* `Documentation/zigux/phase5-trace-events-sample-survey.md`",
                "* `zigux/tests/phase5_trace_events_sample_manifest.json`",
                "* current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
                "",
            ]
        ),
    }

    for relative_path, content in fixture_text.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing(case_name: str, root: Path, expected: str) -> None:
    missing = validate_root(root)
    assert expected in missing, f"{case_name}: expected {expected!r}, got {missing!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase5_shared_guidance_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_tree(tmp_root)

        missing = validate_root(tmp_root)
        assert not missing, missing

        guide_path = tmp_root / "Documentation/zigux/phase5-sample-review-guide.md"
        original_guide = guide_path.read_text(encoding="utf-8")
        guide_path.write_text(
            original_guide.replace(
                "scripts/zigux/README.md",
                "scripts/zigux/README-missing.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "guide_scripts_readme_gap",
            tmp_root,
            "guide:Repeated current-run GitHub-app contents reads for `scripts/zigux/README.md` still returned `Not Found`, so keep that older scripts-root reminder out of the current shared-surface inventory until a fresh reread proves the exact path returned again.",
        )

        write_fixture_tree(tmp_root)
        samples_readme_path = tmp_root / "samples/zigux/README.md"
        original_samples = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            original_samples.replace("* `samples/zigux/kretprobe_example.zig`\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "samples_readme_kretprobe_anchor_gap",
            tmp_root,
            "samples_readme:* `samples/zigux/kretprobe_example.zig`",
        )

        write_fixture_tree(tmp_root)
        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests.replace(
                "* current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_phase5_build_gap",
            tmp_root,
            "tests_readme:* current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
        )

    print("PHASE5_SHARED_SAMPLE_GUIDANCE_SELF_TEST=pass")
    print(
        "PHASE5_SHARED_SAMPLE_GUIDANCE_MARKER_COUNT="
        f"{len(GUIDE_MARKERS) + len(SAMPLES_README_MARKERS) + len(TESTS_README_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 5 sample guidance packet drifts."
    )
    parser.add_argument("--self-test", action="store_true", help="run checker self-test")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="repo root to validate (defaults to current directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate_root(Path(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("PHASE5_SHARED_SAMPLE_GUIDANCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
