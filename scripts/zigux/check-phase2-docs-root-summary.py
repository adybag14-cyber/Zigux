#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_ARTIFACT_TOOLS_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
)

REQUIRED_FILES = (
    DOCS_ROOT_README,
    PHASE2_CLOSURE,
    PHASE2_BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    PHASE2_TOOL_MANIFEST,
    PHASE2_ARTIFACT_TOOLS_MANIFEST,
)

REQUIRED_DOCS_ROOT_MARKERS = (
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/Makefile` keep the bounded Phase 2 docs-root packet explicit",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet",
)

EXACT_COUNT_MARKERS = (
    "Phase 2 notes",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
)

EXPECTED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

EXPECTED_CHECKER_SURFACES = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(path: Path) -> dict[str, object]:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise SystemExit(f"required manifest has invalid top-level shape: {path}")
    return payload


def collect_manifest_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        merged: set[str] = set()
        for item in value:
            merged.update(collect_manifest_strings(item))
        return merged
    if isinstance(value, dict):
        merged: set[str] = set()
        for item in value.values():
            merged.update(collect_manifest_strings(item))
        return merged
    return set()


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    resolved_files = [root / path.relative_to(ROOT) for path in REQUIRED_FILES]
    for path in resolved_files:
        if not path.exists():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(root))))

    if issues:
        return issues

    docs_text = read_text(root / DOCS_ROOT_README.relative_to(ROOT))
    for marker in REQUIRED_DOCS_ROOT_MARKERS:
        if marker not in docs_text:
            issues.append(("MISSING_DOCS_ROOT_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        count = docs_text.count(marker)
        if count != 1:
            issues.append(("DOCS_ROOT_MARKER_COUNT", f"{count}::{marker}"))

    manifest = read_manifest(root / PHASE2_TOOL_MANIFEST.relative_to(ROOT))
    manifest_strings = collect_manifest_strings(manifest)

    for surface in EXPECTED_REVIEW_SURFACES:
        if surface not in manifest_strings:
            issues.append(("MISSING_MANIFEST_REVIEW_SURFACE", surface))

    for surface in EXPECTED_CHECKER_SURFACES:
        if surface not in manifest_strings:
            issues.append(("MISSING_MANIFEST_CHECKER_SURFACE", surface))

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_PHASE2_TOOL_MANIFEST_GAPS", json.dumps(manifest.get("repo_reality_gaps"))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_DOCS_ROOT_SUMMARY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root / DOCS_ROOT_README.relative_to(ROOT), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    for path in (
        PHASE2_CLOSURE,
        PHASE2_BOOTSTRAP_NOTES,
        REVIEW_CHECKLIST,
        SCRIPTS_README,
        TESTS_README,
        MAKEFILE,
        PHASE2_ARTIFACT_TOOLS_MANIFEST,
    ):
        write_text(root / path.relative_to(ROOT), "present\n")

    manifest = {
        "phase": "Phase 2",
        "present_surfaces": {
            "review_surfaces": list(EXPECTED_REVIEW_SURFACES),
            "checkers": list(EXPECTED_CHECKER_SURFACES),
        },
        "repo_reality_gaps": [],
    }
    write_text(
        root / PHASE2_TOOL_MANIFEST.relative_to(ROOT),
        json.dumps(manifest, indent=2) + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_root_summary_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        docs_path = root / DOCS_ROOT_README.relative_to(ROOT)

        for marker in (
            REQUIRED_DOCS_ROOT_MARKERS[0],
            REQUIRED_DOCS_ROOT_MARKERS[7],
            REQUIRED_DOCS_ROOT_MARKERS[18],
            REQUIRED_DOCS_ROOT_MARKERS[-1],
        ):
            build_sample_root(root)
            docs_path.write_text(replace_once(read_text(docs_path), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKER", marker) in issues
            checks_run += 1

        build_sample_root(root)
        docs_path.write_text(read_text(docs_path) + EXACT_COUNT_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("DOCS_ROOT_MARKER_COUNT", f"2::{EXACT_COUNT_MARKERS[0]}") in issues
        checks_run += 1

        build_sample_root(root)
        manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        manifest = read_manifest(manifest_path)
        manifest["present_surfaces"]["review_surfaces"] = manifest["present_surfaces"]["review_surfaces"][1:]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_REVIEW_SURFACE", EXPECTED_REVIEW_SURFACES[0]) in issues
        checks_run += 1

        build_sample_root(root)
        manifest = read_manifest(manifest_path)
        manifest["present_surfaces"]["checkers"] = manifest["present_surfaces"]["checkers"][1:]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_CHECKER_SURFACE", EXPECTED_CHECKER_SURFACES[0]) in issues
        checks_run += 1

        build_sample_root(root)
        manifest = read_manifest(manifest_path)
        manifest["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("NONEMPTY_PHASE2_TOOL_MANIFEST_GAPS", '["gap"]') in issues
        checks_run += 1

    print("PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the shared Phase 2 docs-root summary packet against drift."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in contract self-test instead of repo validation",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a current-like sample root for focused replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_DOCS_ROOT_SUMMARY_SAMPLE_ROOT=written")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_ROOT_SUMMARY=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_MARKER_COUNT={len(REQUIRED_DOCS_ROOT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
