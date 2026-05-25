#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

README_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`zigux/Makefile`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

MAKEFILE_ROUTES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

MANIFEST_SURFACES = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/artifact_diff.py",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "third_party/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_strings(item))
        return strings
    return set()


def collect_missing(text: str, markers: tuple[str, ...], code: str, label: str) -> list[tuple[str, str]]:
    return [(code, f"{label}::{marker}") for marker in markers if marker not in text]


def collect_manifest_missing(strings: set[str]) -> list[tuple[str, str]]:
    return [
        ("MISSING_MANIFEST_SURFACES", surface)
        for surface in MANIFEST_SURFACES
        if surface not in strings
    ]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_text = read_text(resolve_path(root, DOCS_README))
    scripts_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_text = read_text(resolve_path(root, TESTS_README))
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    manifest = read_manifest(resolve_path(root, PHASE2_TOOL_MANIFEST))
    manifest_strings = collect_strings(manifest)

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(docs_text, README_MARKERS, "MISSING_README_MARKERS", "Documentation/zigux/README.md"))
    issues.extend(collect_missing(scripts_text, README_MARKERS, "MISSING_README_MARKERS", "scripts/zigux/README.md"))
    issues.extend(collect_missing(tests_text, README_MARKERS, "MISSING_README_MARKERS", "zigux/tests/README.md"))
    issues.extend(collect_missing(closure_text, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS", "Documentation/zigux/phase2-closure.md"))
    issues.extend(collect_missing(makefile_text, MAKEFILE_ROUTES, "MISSING_MAKEFILE_ROUTES", "zigux/Makefile"))
    issues.extend(collect_manifest_missing(manifest_strings))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_MANIFEST_GAPS", json.dumps(manifest.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SHARED_README_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    readme_text = "\n".join(README_MARKERS) + "\n"
    closure_text = "\n".join(CLOSURE_MARKERS) + "\n"
    makefile_text = "\n".join(MAKEFILE_ROUTES) + "\n"
    manifest_text = json.dumps(
        {
            "phase": "Phase 2",
            "present_surfaces": {"all": list(MANIFEST_SURFACES)},
            "repo_reality_gaps": [],
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
    write_text(resolve_path(root, DOCS_README), readme_text)
    write_text(resolve_path(root, SCRIPTS_README), readme_text)
    write_text(resolve_path(root, TESTS_README), readme_text)
    write_text(resolve_path(root, PHASE2_CLOSURE), closure_text)
    write_text(resolve_path(root, MAKEFILE), makefile_text)
    write_text(resolve_path(root, PHASE2_TOOL_MANIFEST), manifest_text)


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(README_MARKERS) * 3
        + len(CLOSURE_MARKERS)
        + len(MAKEFILE_ROUTES)
        + len(MANIFEST_SURFACES)
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_shared_readme_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        for rel_path in (DOCS_README, SCRIPTS_README, TESTS_README):
            for marker in README_MARKERS:
                build_self_test_root(root)
                path = resolve_path(root, rel_path)
                write_text(path, remove_once(read_text(path), marker))
                issues = collect_issues(root)
                expected = ("MISSING_README_MARKERS", f"{rel_path.relative_to(ROOT)}::{marker}")
                assert expected in issues, (expected, issues)
                checks_run += 1

        for marker in CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            expected = ("MISSING_CLOSURE_MARKERS", f"{PHASE2_CLOSURE.relative_to(ROOT)}::{marker}")
            assert expected in issues, (expected, issues)
            checks_run += 1

        for marker in MAKEFILE_ROUTES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, remove_once(read_text(path), marker))
            issues = collect_issues(root)
            expected = ("MISSING_MAKEFILE_ROUTES", f"{MAKEFILE.relative_to(ROOT)}::{marker}")
            assert expected in issues, (expected, issues)
            checks_run += 1

        for surface in MANIFEST_SURFACES:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_TOOL_MANIFEST)
            manifest = read_manifest(path)
            manifest["present_surfaces"]["all"] = [
                item for item in manifest["present_surfaces"]["all"] if item != surface
            ]
            write_text(path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            issues = collect_issues(root)
            expected = ("MISSING_MANIFEST_SURFACES", surface)
            assert expected in issues, (expected, issues)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        manifest = read_manifest(path)
        manifest["repo_reality_gaps"] = ["gap"]
        write_text(path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert ("NONEMPTY_MANIFEST_GAPS", json.dumps(["gap"])) in issues, issues
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"self-test count drift: expected {expected_case_count}, got {checks_run}")

    print("PHASE2_SHARED_README_PACKET=self-test-pass")
    print(f"PHASE2_SHARED_README_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 docs-root, scripts-root, and tests-root reminder packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in regression checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SHARED_README_PACKET=pass")
    print(f"PHASE2_SHARED_README_PACKET_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_SHARED_README_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_SHARED_README_PACKET_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_ROUTES)}")
    print(f"PHASE2_SHARED_README_PACKET_MANIFEST_SURFACE_COUNT={len(MANIFEST_SURFACES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
