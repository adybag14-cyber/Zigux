#!/usr/bin/env python3
"""Guard the current Phase 2 artifact-diff support packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS_README = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
ARTIFACT_MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
ARTIFACT_HELPER = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_MANIFEST_CHECKER = Path("scripts/zigux/check-phase2-artifact-tools-manifest.py")
KCONFIG_CONSUMER = Path("scripts/zigux/check-kconfig-bridge.py")
FIXDEP_CONSUMER = Path("scripts/zigux/check-fixdep-diff.py")

REQUIRED_PATHS = (
    DOCS_README,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    VALIDATE_PHASE2,
    ARTIFACT_MANIFEST,
    ARTIFACT_HELPER,
    ARTIFACT_MANIFEST_CHECKER,
    KCONFIG_CONSUMER,
    FIXDEP_CONSUMER,
)

REQUIRED_TEXT_MARKERS = {
    DOCS_README: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
        "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    ),
    BOOTSTRAP_NOTES: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
        "`scripts/zigux/artifact_diff.py` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    ),
    PHASE2_CLOSURE: (
        "This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, bootstrap-workflow-routes, kconfig-bridge, helper-local allconfig guard, genksyms bridge, fixdep, make-wrapper, manifest-guard, artifact-diff helper, and validator surfaces on current `master`.",
        "keeps the artifact-support helper packet explicit through `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-fixdep-diff.py`, and `make -C zigux phase2-tools`",
    ),
    REVIEW_CHECKLIST: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "`make -C zigux phase2-tools`",
    ),
    SCRIPTS_README: (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`scripts/zigux/artifact_diff.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "artifact-support",
    ),
    VALIDATE_PHASE2: (
        '"scripts/zigux/artifact_diff.py",',
        '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
        '"zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
    ),
    ARTIFACT_MANIFEST: (
        '"scope": "artifact-diff support for fixture-backed scripts/zigux validation"',
        '"scripts/zigux/artifact_diff.py"',
        '"scripts/zigux/check-kconfig-bridge.py"',
        '"scripts/zigux/check-fixdep-diff.py"',
        '"supported_modes": [',
        '"bytes"',
        'legacy `sha256` compatibility alias',
    ),
    ARTIFACT_HELPER: (
        'MODE_CHOICES = ("text", "json", "bytes")',
        'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
        '"legacy_sha256_alias",',
        "def normalize_mode(mode: str) -> str:",
        "return LEGACY_MODE_ALIASES.get(mode, mode)",
    ),
    ARTIFACT_MANIFEST_CHECKER: (
        'REQUIRED_TOOLING = {',
        '"checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],',
        "PRIMARY_TOOL_MARKERS = (",
        "EXPECTED_CONSUMER_MARKERS = {",
    ),
    KCONFIG_CONSUMER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))',
        'run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))',
    ),
    FIXDEP_CONSUMER: (
        'ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"',
        'diff_text(expected_stdout, zig_actual)',
        'diff_text(expected_stdout, zig_repeat)',
        'diff_text(zig_actual, zig_repeat)',
        'diff_text(expected_stderr_path, zig_actual_stderr)',
        'diff_text(expected_stderr_path, zig_repeat_stderr)',
        'diff_text(zig_actual_stderr, zig_repeat_stderr)',
    ),
}

FORBIDDEN_TEXT_MARKERS = {
    BOOTSTRAP_NOTES: (
        "missing-current-master gaps",
    ),
    PHASE2_CLOSURE: (
        "repo-reality-gap bucket",
    ),
}

EXPECTED_SELF_TEST_CASE_COUNT = 23


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_marker_issues(text: str, label: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_occurrences(text, marker)
        if count == 0:
            issues.append(("MISSING_MARKER", f"{label}:{marker}"))
        elif count != 1:
            issues.append(("DUPLICATE_MARKER", f"{label}:{marker}:count={count}"))
    return issues


def collect_forbidden_issues(text: str, label: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker in text:
            issues.append(("FORBIDDEN_MARKER", f"{label}:{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        path = resolve(root, rel)
        if not path.exists():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))
            continue
        text = read_text(path)
        issues.extend(collect_marker_issues(text, rel.as_posix(), REQUIRED_TEXT_MARKERS[rel]))
        forbidden = FORBIDDEN_TEXT_MARKERS.get(rel, ())
        issues.extend(collect_forbidden_issues(text, rel.as_posix(), forbidden))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_DIFF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel, markers in REQUIRED_TEXT_MARKERS.items():
        content = "\n".join(markers) + "\n"
        write_text(resolve(root, rel), content)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_diff_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for rel in (DOCS_README, BOOTSTRAP_NOTES, PHASE2_CLOSURE, REVIEW_CHECKLIST, SCRIPTS_README, VALIDATE_PHASE2, ARTIFACT_MANIFEST, ARTIFACT_HELPER, KCONFIG_CONSUMER, FIXDEP_CONSUMER):
            build_sample_root(root)
            target = resolve(root, rel)
            marker = REQUIRED_TEXT_MARKERS[rel][0]
            write_text(target, replace_once(read_text(target), marker, ""))
            assert ("MISSING_MARKER", f"{rel.as_posix()}:{marker}") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        target = resolve(root, ARTIFACT_HELPER)
        marker = REQUIRED_TEXT_MARKERS[ARTIFACT_HELPER][0]
        write_text(target, read_text(target) + marker + "\n")
        assert ("DUPLICATE_MARKER", f"{ARTIFACT_HELPER.as_posix()}:{marker}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        target = resolve(root, BOOTSTRAP_NOTES)
        forbidden = FORBIDDEN_TEXT_MARKERS[BOOTSTRAP_NOTES][0]
        write_text(target, read_text(target) + forbidden + "\n")
        assert ("FORBIDDEN_MARKER", f"{BOOTSTRAP_NOTES.as_posix()}:{forbidden}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        target = resolve(root, PHASE2_CLOSURE)
        forbidden = FORBIDDEN_TEXT_MARKERS[PHASE2_CLOSURE][0]
        write_text(target, read_text(target) + forbidden + "\n")
        assert ("FORBIDDEN_MARKER", f"{PHASE2_CLOSURE.as_posix()}:{forbidden}") in collect_issues(root)
        checks += 1

        for rel in (ARTIFACT_MANIFEST_CHECKER, REVIEW_CHECKLIST, SCRIPTS_README, VALIDATE_PHASE2, ARTIFACT_MANIFEST, ARTIFACT_HELPER, KCONFIG_CONSUMER, FIXDEP_CONSUMER):
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_PATH", rel.as_posix()) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        target = resolve(root, ARTIFACT_MANIFEST_CHECKER)
        marker = REQUIRED_TEXT_MARKERS[ARTIFACT_MANIFEST_CHECKER][1]
        write_text(target, replace_once(read_text(target), marker, marker + "\n" + marker))
        assert ("DUPLICATE_MARKER", f"{ARTIFACT_MANIFEST_CHECKER.as_posix()}:{marker}:count=2") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, (checks, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract tests")
    parser.add_argument("--write-sample-root", type=Path, help="Write a focused current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARTIFACT_DIFF_PACKET=pass")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_ARTIFACT_DIFF_PACKET_TEXT_SURFACE_COUNT={len(REQUIRED_TEXT_MARKERS)}")
    print("PHASE2_ARTIFACT_DIFF_PACKET_CONSUMER_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
