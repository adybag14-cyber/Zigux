#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REQUIRED_TESTS_README_MARKERS = (
    "Phase 2 review packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, toolchain reminder, toolchain pin-scope, required-make-route, and direct toolchain-checker set plus the live kconfig bridge helpers, the shipped `zigux/Makefile` wrappers, and the current fixture roster",
    "keep the pinned `x86_64-linux` bootstrap archive note and repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py`, pin-scope, and required-make-route guards explicit in this tests-root packet beside the shipped `zigux/Makefile` wrappers",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or direct cross-route proof text",
)
FORBIDDEN_TESTS_README_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`",
    "repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`",
    "keep the fixture-backed cross-target, tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)
REQUIRED_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "now keep the current directly readable Phase 2 toolchain, kbuild, and kconfig bridge packet visible from the docs root",
    "keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the pinned Zig toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, the current kconfig fixture roster, and the current reminder routes `make -C zigux phase2-validate` plus `make -C zigux phase2`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    issues = collect_missing_markers(
        tests_readme_text,
        REQUIRED_TESTS_README_MARKERS,
        "MISSING_TESTS_README_MARKERS",
    )
    issues.extend(
        collect_forbidden_markers(
            tests_readme_text,
            FORBIDDEN_TESTS_README_MARKERS,
            "FORBIDDEN_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            docs_root_text,
            REQUIRED_DOCS_ROOT_MARKERS,
            "MISSING_DOCS_ROOT_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TESTS_README_ALIGNMENT=fail")
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
    write_text(resolve_path(root, TESTS_README), "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")


def replace_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
        + len(REQUIRED_DOCS_ROOT_MARKERS)
    )
    with tempfile.TemporaryDirectory(prefix="zigux_p2_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        for marker in REQUIRED_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1
        for marker in FORBIDDEN_TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_README_MARKERS", marker) in issues
            checks_run += 1
        for marker in REQUIRED_DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKERS", marker) in issues
            checks_run += 1
    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the restored Phase 2 tests-root packet aligned with the current docs-root reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_ALIGNMENT_DOCS_ROOT_MARKER_COUNT={len(REQUIRED_DOCS_ROOT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
