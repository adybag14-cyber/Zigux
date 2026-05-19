#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")

REQUIRED_TEXT = (
    "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.",
    "while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
    "keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh reread restores direct authenticated proof for those two routes.",
)

REQUIRED_PATHS = (
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "samples/zigux/kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
    "samples/zigux/runtime_*.zig",
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
    "zigux/tests/phase5_build.zig",
)

FORBIDDEN_TEXT = (
    "treat `samples/zigux/runtime_*.zig` as extra Phase 5 proof",
    "returned full trace-events port or a fifth sample outside the bounded formatting companion",
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
    docs_root = _read(root / DOCS_ROOT_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in docs_root:
            failures.append(f"docs_root:missing_text:{marker}")

    for rel in REQUIRED_PATHS:
        if f"`{rel}`" not in docs_root:
            failures.append(f"docs_root:missing_path:`{rel}`")

    lowered = docs_root.lower()
    for text in FORBIDDEN_TEXT:
        if text.lower() in lowered:
            failures.append(f"docs_root:forbidden_text:{text}")

    return failures


def _sample_docs_root() -> str:
    packet_paths = "\n".join(f"- `{rel}`" for rel in REQUIRED_PATHS[:11])
    return f"""# Zigux Documentation
Phase 5 notes
{packet_paths}
{REQUIRED_TEXT[0]}
  * current `master` still directly exposes the restored bytestream packet through `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`, and it still directly exposes the restored kretprobe packet through `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.
  * {REQUIRED_TEXT[2]}
  * {REQUIRED_TEXT[3]}
  * {REQUIRED_TEXT[4]}
  * {REQUIRED_TEXT[5]}
"""


def _seed(root: Path) -> None:
    _write(root / DOCS_ROOT_PATH, _sample_docs_root())


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 5
    with tempfile.TemporaryDirectory(prefix="phase5_docs_root_phase_boundaries_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_runtime_boundary_root = root / "missing_runtime_boundary"
        _seed(missing_runtime_boundary_root)
        _write(
            missing_runtime_boundary_root / DOCS_ROOT_PATH,
            _sample_docs_root().replace(REQUIRED_TEXT[4], "", 1),
        )
        failures = collect_failures(missing_runtime_boundary_root)
        expected = [
            f"docs_root:missing_text:{REQUIRED_TEXT[4]}",
            "docs_root:missing_path:`samples/zigux/runtime_*.zig`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-runtime-boundary failure: {failures}")
        checks_run += 1

        missing_checker_guard_root = root / "missing_checker_guard"
        _seed(missing_checker_guard_root)
        _write(
            missing_checker_guard_root / DOCS_ROOT_PATH,
            _sample_docs_root().replace(REQUIRED_TEXT[2], "", 1),
        )
        failures = collect_failures(missing_checker_guard_root)
        expected = [f"docs_root:missing_text:{REQUIRED_TEXT[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker-guard failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(
            forbidden_text_root / DOCS_ROOT_PATH,
            _sample_docs_root() + "\nTreat `samples/zigux/runtime_*.zig` as extra Phase 5 proof.\n",
        )
        failures = collect_failures(forbidden_text_root)
        expected = ["docs_root:forbidden_text:treat `samples/zigux/runtime_*.zig` as extra Phase 5 proof"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

        missing_docs_root_root = root / "missing_docs_root"
        _seed(missing_docs_root_root)
        (missing_docs_root_root / DOCS_ROOT_PATH).unlink()
        try:
            collect_failures(missing_docs_root_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-docs-root abort: {exc}") from exc
        else:
            raise AssertionError("missing docs root did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")

    print("PHASE5_DOCS_ROOT_PHASE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE5_DOCS_ROOT_PHASE_BOUNDARIES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 docs-root reminder keeps current sample and phase-boundary wording explicit."
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

    print("PHASE5_DOCS_ROOT_PHASE_BOUNDARIES=pass")
    print(f"PHASE5_DOCS_ROOT_PHASE_BOUNDARIES_REQUIRED_TEXT_COUNT={len(REQUIRED_TEXT)}")
    print(f"PHASE5_DOCS_ROOT_PHASE_BOUNDARIES_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
