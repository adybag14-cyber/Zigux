#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) >= 4 else Path.cwd()
NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

REQUIRED_MARKERS = (
    "# Zigux Artifact-Diff Notes",
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
    "`zigux/tests/fixtures/fixdep/cases.json` keeps the current twelve-case fixdep packet reviewable by naming the committed stdout artifact for every shipped case and the expected stderr or exit-code contract whenever the case is not a plain success path, including the dedicated `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full` write-failure replays.",
    "`scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`.",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` anchors the smallest wrapper-first `genksyms` invocation claim.",
    "`scripts/zigux/check-genksyms-bridge.py` compares those committed JSON fixtures against both a bounded C harness and `scripts/zigux/genksyms.zig`.",
    "`scripts/zigux/check-kconfig-bridge.py` compares those committed JSON fixtures against `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`.",
    "`zigux/tests/fixtures/phase2_cross_targets.json` fixes the bounded cross-target compile set for the Phase 2 tool tranche.",
    "`scripts/zigux/check-mk-elfconfig-diff.py` compares those committed JSON results against both the C tool and `scripts/zigux/mk_elfconfig.zig`.",
)

FORBIDDEN_MARKERS: tuple[str, ...] = ()

EXACT_COUNT_MARKERS = REQUIRED_MARKERS[2:]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_issues(root: Path) -> list[tuple[str, str]]:
    note_text = read_text(resolve_path(root, NOTE))
    issues: list[tuple[str, str]] = []
    issues.extend(("MISSING_MARKER", marker) for marker in REQUIRED_MARKERS if marker not in note_text)
    issues.extend(("FORBIDDEN_MARKER", marker) for marker in FORBIDDEN_MARKERS if marker in note_text)
    for marker in EXACT_COUNT_MARKERS:
        count = note_text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_MARKER", f"{count}::{marker}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_DIFF_NOTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_note_text() -> str:
    return "\n".join(
        (
            "# Zigux Artifact-Diff Notes",
            "",
            "## Current Phase 2 use",
            "",
            REQUIRED_MARKERS[2],
            REQUIRED_MARKERS[3],
            REQUIRED_MARKERS[4],
            REQUIRED_MARKERS[5],
            REQUIRED_MARKERS[6],
            REQUIRED_MARKERS[7],
            REQUIRED_MARKERS[8],
            REQUIRED_MARKERS[9],
            "",
        )
    )


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, NOTE), sample_note_text())


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + len(FORBIDDEN_MARKERS) + len(EXACT_COUNT_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_diff_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MARKER", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, NOTE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MARKER", marker) in issues
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, NOTE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_MARKER", f"2::{marker}") in issues
            checks_run += 1

        build_sample_root(root)
        resolve_path(root, NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing note did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 artifact-diff note aligned with the current fixture-backed consumer packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_NOTE=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_REQUIRED_PATH_COUNT={13}")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
