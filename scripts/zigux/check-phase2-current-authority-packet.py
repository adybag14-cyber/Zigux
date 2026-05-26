#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"

REQUIRED_MARKERS = (
    "## Status",
    "## Current Closure Packet",
    "current authority: this closure note, the committed Phase 2 tool manifest, the toolchain bootstrap note, the live toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, reminder, pinning, manifest, artifact helper, fixdep guards, the helper-local kconfig allconfig guard, the returned closure-side validator pair, the shipped `zigux/Makefile` wrappers, and the current kconfig, genksyms, fixdep, artifact-support, plus cross-route fixture manifests remain the trustworthy current-master sources for the bounded Phase 2 tranche",
    "The bounded Phase 2 tranche remains the directly readable toolchain, local-first archive, archive-verification, staged repo-local archive helper contract and selftest packet, installer, direct cross-route, selected kconfig-bridge plus helper-local allconfig guard, bounded genksyms bridge, direct standalone genksyms invalid-long-option and ambiguous-long-option version-side-effect proofs, fixdep, required-make-route, validator-entrypoint, closure-validator, and fixture-backed artifact-support packet already present on current `master`.",
)

REQUIRED_AUTHORITY_SURFACES = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

EXACT_COUNT_MARKERS = (
    "current authority:",
    "the committed Phase 2 tool manifest",
    "the returned closure-side validator pair",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, CLOSURE_NOTE))
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_CURRENT_AUTHORITY_MARKERS", marker))
    for surface in REQUIRED_AUTHORITY_SURFACES:
        if surface not in text:
            issues.append(("MISSING_CURRENT_AUTHORITY_SURFACES", surface))
    for marker in EXACT_COUNT_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_CURRENT_AUTHORITY_MARKERS", f"{count}::{marker}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CURRENT_AUTHORITY_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    lines = list(REQUIRED_MARKERS) + list(REQUIRED_AUTHORITY_SURFACES)
    write_text(resolve_path(root, CLOSURE_NOTE), "\n".join(lines) + "\n")


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + len(REQUIRED_AUTHORITY_SURFACES) + len(EXACT_COUNT_MARKERS)
    with tempfile.TemporaryDirectory(prefix="zigux_p2_current_authority_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        note_path = resolve_path(root, CLOSURE_NOTE)
        text = read_text(note_path)

        for marker in REQUIRED_MARKERS:
            write_text(note_path, remove_all(text, marker))
            issues = collect_issues(root)
            assert ("MISSING_CURRENT_AUTHORITY_MARKERS", marker) in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(note_path)
            checks_run += 1

        for surface in REQUIRED_AUTHORITY_SURFACES:
            write_text(note_path, remove_all(text, surface))
            issues = collect_issues(root)
            assert ("MISSING_CURRENT_AUTHORITY_SURFACES", surface) in issues, (surface, issues)
            build_sample_root(root)
            text = read_text(note_path)
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_text(note_path, text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_CURRENT_AUTHORITY_MARKERS", f"2::{marker}") in issues, (marker, issues)
            build_sample_root(root)
            text = read_text(note_path)
            checks_run += 1

        if checks_run != expected_case_count:
            raise AssertionError(
                f"self-test count drift: expected {expected_case_count}, got {checks_run}"
            )

    print("PHASE2_CURRENT_AUTHORITY_PACKET=self-test-pass")
    print(f"PHASE2_CURRENT_AUTHORITY_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regression checks instead of repo validation.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to current repo root).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_CURRENT_AUTHORITY_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CURRENT_AUTHORITY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
