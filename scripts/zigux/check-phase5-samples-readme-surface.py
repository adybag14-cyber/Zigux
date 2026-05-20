#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLES_ROOT_PATH = Path("samples/zigux/README.md")

DIRECT_SAMPLE_PATHS = (
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/kobject_example.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
)

DIRECT_COMPANION_PATHS = (
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
)

PUBLIC_TREE_COMPANION_PATHS = (
    "zigux/tests/phase5_kobject_example_survey.zig",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

REQUIRED_TEXT = (
    "The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:",
    "Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.",
    "Current `master` keeps the kobject sample-root port directly readable in `samples/zigux/` through `samples/zigux/kobject_example.zig`.",
    "Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.",
    "Keep the kobject anchor framed as a roadmap-backed Phase 5 target with a mixed direct-plus-public-tree-backed packet: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread returns them directly too.",
    "For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet.",
    "Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.",
    "Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; cmdline reviewability remains under `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_cmdline_survey.zig` rather than the four shipped Phase 5 samples.",
    "Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, bitmap, `printf`, `vsprintf`, or broad `format` sample families landed here as standalone samples.",
    "Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.",
)

NO_EXTRA_SAMPLE_MARKERS = (
    "* `*string*`",
    "* `*cmdline*`",
    "* `*argv*`",
    "* `*rbtree*`",
    "* `*kasprintf*`",
    "* `*strarray*`",
    "* `*bitmap*`",
    "* `*printf*`",
    "* `*vsprintf*`",
    "* `*format*`",
)

FORBIDDEN_TEXT = (
    "Do count it as a fifth approved Phase 5 anchor.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 proof.",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _bullet_list(paths: tuple[str, ...]) -> str:
    return "\n".join(f"* `{path}`" for path in paths)


def collect_failures(root: Path) -> list[str]:
    samples_root = _read(root / SAMPLES_ROOT_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in samples_root:
            failures.append(f"samples_root:missing_text:{marker}")

    for marker in NO_EXTRA_SAMPLE_MARKERS:
        if marker not in samples_root:
            failures.append(f"samples_root:missing_boundary:{marker}")

    for rel in DIRECT_SAMPLE_PATHS:
        if f"`{rel}`" not in samples_root:
            failures.append(f"samples_root:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in DIRECT_COMPANION_PATHS:
        if f"`{rel}`" not in samples_root:
            failures.append(f"samples_root:missing_companion_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_companion_path:{rel}")

    for rel in PUBLIC_TREE_COMPANION_PATHS:
        if f"`{rel}`" not in samples_root:
            failures.append(f"samples_root:missing_public_tree_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_public_tree_path:{rel}")

    for text in FORBIDDEN_TEXT:
        if text in samples_root:
            failures.append(f"samples_root:forbidden_text:{text}")

    return failures


def _sample_samples_root() -> str:
    sections = [
        "# samples/zigux",
        "",
        *REQUIRED_TEXT,
        "",
        _bullet_list(DIRECT_SAMPLE_PATHS),
        "",
        _bullet_list(DIRECT_COMPANION_PATHS),
        "",
        _bullet_list(PUBLIC_TREE_COMPANION_PATHS),
        "",
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "",
        *NO_EXTRA_SAMPLE_MARKERS,
        "",
    ]
    return "\n".join(sections) + "\n"


def _seed(root: Path) -> None:
    _write(root / SAMPLES_ROOT_PATH, _sample_samples_root())
    for rel in DIRECT_SAMPLE_PATHS + DIRECT_COMPANION_PATHS + PUBLIC_TREE_COMPANION_PATHS:
        if Path(rel) == SAMPLES_ROOT_PATH:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_samples_readme_surface_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_required_text_root = root / "missing_required_text"
        _seed(missing_required_text_root)
        _write(
            missing_required_text_root / SAMPLES_ROOT_PATH,
            _sample_samples_root().replace(REQUIRED_TEXT[4], "", 1),
        )
        failures = collect_failures(missing_required_text_root)
        expected = [f"samples_root:missing_text:{REQUIRED_TEXT[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-required-text failure: {failures}")
        checks_run += 1

        missing_boundary_root = root / "missing_boundary"
        _seed(missing_boundary_root)
        _write(
            missing_boundary_root / SAMPLES_ROOT_PATH,
            _sample_samples_root().replace(NO_EXTRA_SAMPLE_MARKERS[3], "", 1),
        )
        failures = collect_failures(missing_boundary_root)
        expected = [f"samples_root:missing_boundary:{NO_EXTRA_SAMPLE_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-boundary failure: {failures}")
        checks_run += 1

        missing_companion_path_marker_root = root / "missing_companion_path_marker"
        _seed(missing_companion_path_marker_root)
        _write(
            missing_companion_path_marker_root / SAMPLES_ROOT_PATH,
            _sample_samples_root().replace("`zigux/tests/phase5_bytestream_fifo_manifest.json`", "", 1),
        )
        failures = collect_failures(missing_companion_path_marker_root)
        expected = ["samples_root:missing_companion_path:`zigux/tests/phase5_bytestream_fifo_manifest.json`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-companion-path-marker failure: {failures}")
        checks_run += 1

        missing_direct_file_root = root / "missing_direct_file"
        _seed(missing_direct_file_root)
        (missing_direct_file_root / "samples/zigux/kretprobe_example.zig").unlink()
        failures = collect_failures(missing_direct_file_root)
        expected = ["repo:missing_direct_path:samples/zigux/kretprobe_example.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-file failure: {failures}")
        checks_run += 1

        missing_public_tree_file_root = root / "missing_public_tree_file"
        _seed(missing_public_tree_file_root)
        (missing_public_tree_file_root / "zigux/tests/phase5_trace_events_sample_manifest.json").unlink()
        failures = collect_failures(missing_public_tree_file_root)
        expected = ["repo:missing_public_tree_path:zigux/tests/phase5_trace_events_sample_manifest.json"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-public-tree-file failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(forbidden_text_root / SAMPLES_ROOT_PATH, _sample_samples_root() + FORBIDDEN_TEXT[1] + "\n")
        failures = collect_failures(forbidden_text_root)
        expected = [f"samples_root:forbidden_text:{FORBIDDEN_TEXT[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_SAMPLES_README_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_SAMPLES_README_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 sample-root README stays aligned with the current shared sample packet."
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
    print("PHASE5_SAMPLES_README_SURFACE=pass")
    print(f"PHASE5_SAMPLES_README_SURFACE_DIRECT_SAMPLE_COUNT={len(DIRECT_SAMPLE_PATHS)}")
    print(f"PHASE5_SAMPLES_README_SURFACE_DIRECT_COMPANION_COUNT={len(DIRECT_COMPANION_PATHS)}")
    print(f"PHASE5_SAMPLES_README_SURFACE_PUBLIC_TREE_COMPANION_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    print(f"PHASE5_SAMPLES_README_SURFACE_BOUNDARY_COUNT={len(NO_EXTRA_SAMPLE_MARKERS)}")
    print(f"PHASE5_SAMPLES_README_SURFACE_REQUIRED_TEXT_COUNT={len(REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
