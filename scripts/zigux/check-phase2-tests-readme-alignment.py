#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

DOCS_ROOT_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "- `scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
    "the repo-local `.zig-toolchain` fallback reused by those Linux-style Phase 2 routes when `ZIG` is unset stays explicit here",
    "The broader Phase 2 fixdep, genksyms, kconfig bridge, artifact-tools, manifest, cross-target, and closure-route inventory should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile`.",
)

TESTS_README_MARKERS = (
    "Phase 2 review packet",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`make -C zigux phase2-cross`",
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset",
)

SHARED_ROUTE_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`make -C zigux phase2-cross`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 21


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))

    issues.extend(
        collect_missing_markers(
            docs_root_text,
            DOCS_ROOT_MARKERS,
            "MISSING_DOCS_ROOT_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )

    for marker in SHARED_ROUTE_MARKERS:
        if marker in docs_root_text and marker in tests_readme_text:
            continue
        issues.append(("MISSING_SHARED_ROUTE_ALIGNMENT", marker))

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
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        docs_path = resolve_path(root, DOCS_ROOT_README)
        docs_path.write_text(
            replace_once(
                docs_path.read_text(encoding="utf-8"),
                SHARED_ROUTE_MARKERS[0],
                "`scripts/zigux/check-phase2-other-alignment.py`",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_SHARED_ROUTE_ALIGNMENT", SHARED_ROUTE_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        tests_path = resolve_path(root, TESTS_README)
        tests_path.write_text(
            replace_once(
                tests_path.read_text(encoding="utf-8"),
                SHARED_ROUTE_MARKERS[1],
                "`make -C zigux phase2-other`",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_SHARED_ROUTE_ALIGNMENT", SHARED_ROUTE_MARKERS[1]) in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, DOCS_ROOT_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing docs root did not abort")

        build_self_test_root(root)
        resolve_path(root, TESTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing tests readme did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 docs-root and tests-root reminder packet aligned."
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
    print(f"PHASE2_TESTS_README_ALIGNMENT_DOCS_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
    print(f"PHASE2_TESTS_README_ALIGNMENT_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
