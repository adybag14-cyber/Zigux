#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NOTE_PATH = Path("Documentation/zigux/phase5-kobject-current-readback-note.md")

DIRECT_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_build.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
)

PUBLIC_PATHS = (
    "zigux/tests/phase5_kobject_example_survey.zig",
)

GUIDANCE_PATHS = (
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
)

NOTE_MARKERS = (
    "Authenticated contents readback in this run directly returned:",
    "- `Documentation/zigux/phase5-kobject-sample-survey.md`",
    "- `samples/zigux/kobject_example.zig`",
    "- `zigux/tests/phase5_kobject_example.zig`",
    "- `zigux/tests/phase5_kobject_example_manifest.json`",
    "- `zigux/tests/phase5_build.zig`",
    "Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.",
    "The same run still confirmed this current `master` packet member through public GitHub file readback:",
    "- `zigux/tests/phase5_kobject_example_survey.zig`",
    "- `zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route, and `zigux/tests/phase5_kobject_example_survey.zig` remains part of the same packet even when this run had to prove that survey replay through public current-`master` fallback instead of the authenticated contents route",
    "`Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase5-review-guide-surface.py` already keep the current kobject survey-note inventory explicit, while `samples/zigux/README.md` still frames `zigux/tests/phase5_build.zig` as public-tree-backed companion evidence beside `zigux/tests/phase5_kobject_example_survey.zig` even though the newer guide and sequencing surfaces now treat that shared build route as directly readable for the current packet",
    "`samples/zigux/README.md` as the first same-lane follow-through surface and `scripts/zigux/check-phase5-review-guide-surface.py` as the matching guard only if its `SAMPLE_ROOT_MARKERS[0]` still exact-requires the older sample-root sentence",
    "Compare this note against `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py` the next time the lane reopens.",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_note() -> str:
    direct_lines = "\n".join(f"- `{path}`" for path in DIRECT_PATHS[:-1])
    guidance_inline = ", ".join(f"`{path}`" for path in GUIDANCE_PATHS)
    return f"""# Phase 5 Kobject Current Readback Note

{NOTE_MARKERS[0]}

{direct_lines}

{NOTE_MARKERS[6]}

{NOTE_MARKERS[7]}

{NOTE_MARKERS[8]}

{NOTE_MARKERS[9]}

{NOTE_MARKERS[10]}

{NOTE_MARKERS[11]}

{NOTE_MARKERS[12]}

Guidance packet: {guidance_inline}
"""


def _seed(root: Path) -> None:
    _write(root / NOTE_PATH, _placeholder_note())
    for rel in DIRECT_PATHS + PUBLIC_PATHS + GUIDANCE_PATHS:
        if rel == str(NOTE_PATH):
            continue
        _write(root / rel, "present\n")


def collect_failures(root: Path) -> list[str]:
    note = _read(root / NOTE_PATH)
    failures: list[str] = []

    for marker in NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note:missing_text:{marker}")

    for rel in DIRECT_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"note:missing_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_path:{rel}")

    for rel in PUBLIC_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"note:missing_public_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_public_path:{rel}")

    for rel in GUIDANCE_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"note:missing_guidance_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_guidance_path:{rel}")

    return failures


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 5
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_note_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_public_marker_root = root / "missing_public_marker"
        _seed(missing_public_marker_root)
        _write(
            missing_public_marker_root / NOTE_PATH,
            _placeholder_note().replace(NOTE_MARKERS[8] + "\n\n", ""),
        )
        failures = collect_failures(missing_public_marker_root)
        expected = [f"note:missing_text:{NOTE_MARKERS[8]}"]
        if failures != expected:
            raise AssertionError(f"unexpected public-marker failure: {failures}")
        checks_run += 1

        missing_guidance_marker_root = root / "missing_guidance_marker"
        _seed(missing_guidance_marker_root)
        _write(
            missing_guidance_marker_root / NOTE_PATH,
            _placeholder_note().replace(NOTE_MARKERS[10] + "\n\n", ""),
        )
        failures = collect_failures(missing_guidance_marker_root)
        expected = [f"note:missing_text:{NOTE_MARKERS[10]}"]
        if failures != expected:
            raise AssertionError(f"unexpected guidance-marker failure: {failures}")
        checks_run += 1

        missing_direct_path_root = root / "missing_direct_path"
        _seed(missing_direct_path_root)
        (missing_direct_path_root / DIRECT_PATHS[4]).unlink()
        failures = collect_failures(missing_direct_path_root)
        expected = [f"repo:missing_path:{DIRECT_PATHS[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected direct-path failure: {failures}")
        checks_run += 1

        missing_guidance_path_root = root / "missing_guidance_path"
        _seed(missing_guidance_path_root)
        (missing_guidance_path_root / GUIDANCE_PATHS[-1]).unlink()
        failures = collect_failures(missing_guidance_path_root)
        expected = [f"repo:missing_guidance_path:{GUIDANCE_PATHS[-1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected guidance-path failure: {failures}")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_KOBJECT_CURRENT_READBACK_NOTE_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Phase 5 kobject current-readback note stays aligned with the live direct-versus-public packet split."
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
    print("PHASE5_KOBJECT_CURRENT_READBACK_NOTE=pass")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_DIRECT_COUNT={len(DIRECT_PATHS)}")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_GUIDANCE_COUNT={len(GUIDANCE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
