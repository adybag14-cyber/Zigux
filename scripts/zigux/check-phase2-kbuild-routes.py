#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 kbuild packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    MAKEFILE,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-tools",
)

README_PRESENT_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "the manifest-backed kconfig fixture roster",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2`",
    "`make -C zigux phase2-tools`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

README_WARNING_LINES = (
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
)

README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those installer and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, and `make -C zigux phase2`",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
)

DISALLOWED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(README_PRESENT_MARKERS)
    + len(README_WARNING_LINES)
    + len(README_WARNING_LINES)
    + len(README_FORBIDDEN_MARKERS)
    + 2
    + len(SURFACE_PATHS)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(DISALLOWED_MAKEFILE_LINES)
)


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    readme_text = read_text(resolve_path(root, SCRIPTS_README))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(readme_text, README_PRESENT_MARKERS, "MISSING_README_PRESENT_MARKERS"))
    issues.extend(
        collect_exact_line_issues(
            readme_text,
            README_WARNING_LINES,
            "MISSING_README_WARNING_LINES",
            "DUPLICATE_README_WARNING_LINES",
        )
    )
    issues.extend(collect_forbidden_markers(readme_text, README_FORBIDDEN_MARKERS, "FORBIDDEN_README_MARKERS"))
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINES",
            "DUPLICATE_MAKEFILE_LINES",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            makefile_text,
            DISALLOWED_MAKEFILE_LINES,
            "FORBIDDEN_MAKEFILE_LINES",
        )
    )

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KBUILD_ROUTES=fail")
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
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    readme_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        "- current packet",
        *README_PRESENT_MARKERS,
        *README_WARNING_LINES,
    ]
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            (
                "ZIG ?= zig",
                "ZIGUX_ROOT := ..",
                "",
                *REQUIRED_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    for path in SURFACE_PATHS:
        if path == MAKEFILE:
            continue
        write_text(resolve_path(root, path), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kbuild_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in README_PRESENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_README_PRESENT_MARKERS", marker) in issues
            checks_run += 1

        for marker in README_WARNING_LINES:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed for self-test"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_README_WARNING_LINES", marker) in issues
            checks_run += 1

        for marker in README_WARNING_LINES:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("DUPLICATE_README_WARNING_LINES", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_README_MARKERS", marker) in issues
            checks_run += 1

        for primary_path in (WORKFLOW, SCRIPTS_README):
            build_self_test_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, primary_path)) in str(exc)
            else:
                raise AssertionError("missing primary surface did not abort")
            checks_run += 1

        for rel_path in SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            if rel_path == MAKEFILE:
                try:
                    collect_issues(root)
                except SystemExit as exc:
                    assert "required file missing" in str(exc)
                    assert str(resolve_path(root, rel_path)) in str(exc)
                else:
                    raise AssertionError("missing makefile did not abort")
            else:
                issues = collect_issues(root)
                assert ("MISSING_SURFACE_PATHS", rel_path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed for self-test"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_LINES", marker) in issues
            checks_run += 1

        for marker in DISALLOWED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MAKEFILE_LINES", marker) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KBUILD_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_KBUILD_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current directly readable Phase 2 kbuild packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KBUILD_ROUTES=pass")
    print(f"PHASE2_KBUILD_ROUTE_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KBUILD_ROUTE_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())