#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain and kbuild packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def default_root_from(script_path: Path) -> Path:
    resolved = script_path.resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else Path.cwd()


ROOT = default_root_from(Path(__file__))
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPTS_README = Path("scripts/zigux/README.md")
MAKEFILE = Path("zigux/Makefile")

SURFACE_PATHS = (
    Path("Documentation/zigux/phase2-closure.md"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-lane05-install-zig-archive-verification.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-stage-helper-contract.py"),
    Path("scripts/zigux/check-lane05-stage-helper-selftest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-phase2-bootstrap-workflow-routes.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/fixdep.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"),
    Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/stage-pinned-zig-archive.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/zig-toolchain-policy.json"),
    Path("third_party/README.md"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/cases.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
)

ARCHIVE_SURFACE_PATHS = (
    Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"),
    Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts/manifest.json"),
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: python3 scripts/zigux/validate-phase2.py",
)

README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

README_FORBIDDEN_MARKERS = (
    "still return missing for `scripts/zigux/install-zig.py`",
    "still return missing for `scripts/zigux/validate-phase2-closure.py`",
    "need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

FORBIDDEN_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/fixdep.zig",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def collect_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_readme_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in README_MARKERS:
        if marker not in text:
            issues.append(("MISSING_README_MARKER", marker))
    for marker in README_FORBIDDEN_MARKERS:
        if marker in text:
            issues.append(("FORBIDDEN_README_MARKER", marker))
    return issues


def collect_surface_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in SURFACE_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_SURFACE_PATH", rel.as_posix()))
    if not any((root / rel).exists() for rel in ARCHIVE_SURFACE_PATHS):
        issues.append(
            (
                "MISSING_ARCHIVE_SURFACE",
                " or ".join(rel.as_posix() for rel in ARCHIVE_SURFACE_PATHS),
            )
        )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(root, WORKFLOW)
    readme_text = read_text(root, SCRIPTS_README)
    makefile_text = read_text(root, MAKEFILE)
    issues: list[tuple[str, str]] = []
    issues.extend(collect_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))
    issues.extend(collect_readme_issues(readme_text))
    issues.extend(collect_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))
    for marker in FORBIDDEN_MAKEFILE_LINES:
        if marker in makefile_text:
            issues.append(("FORBIDDEN_MAKEFILE_LINE", marker))
    issues.extend(collect_surface_issues(root))
    return issues


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW, "\n".join(WORKFLOW_LINES) + "\n")
    readme_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        f"- {README_MARKERS[0]}",
        f"- {README_MARKERS[1]}",
        f"- {README_MARKERS[2]}",
        f"- {README_MARKERS[3]}",
        f"- {README_MARKERS[4]}",
        f"- {README_MARKERS[5]}",
        f"- {README_MARKERS[6]}",
    ]
    write_text(root / SCRIPTS_README, "\n".join(readme_lines) + "\n")
    write_text(root / MAKEFILE, "\n".join(("PYTHON ?= python3", "ZIG ?= zig", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", "ZIGUX_ROOT := ..", "", *MAKEFILE_LINES)) + "\n")
    for rel in SURFACE_PATHS:
        if rel == MAKEFILE or rel == SCRIPTS_README or rel == WORKFLOW:
            continue
        write_text(root / rel, "present\n")
    write_text(root / ARCHIVE_SURFACE_PATHS[1], "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(README_MARKERS)
        + len(README_FORBIDDEN_MARKERS)
        + 3
        + (len(SURFACE_PATHS) - 3)
        + 1
        + 1
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(FORBIDDEN_MAKEFILE_LINES)
        + 3
        + 1
    )

    assert default_root_from(Path("/tmp/Zigux/scripts/zigux/check-phase2-kbuild-routes.py")) == Path("/tmp/Zigux")
    checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kbuild_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = root / SCRIPTS_README
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "BROKEN_README_MARKER", 1), encoding="utf-8")
            assert ("MISSING_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = root / SCRIPTS_README
            path.write_text(path.read_text(encoding="utf-8") + f"\n- {marker}\n", encoding="utf-8")
            assert ("FORBIDDEN_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for rel in (WORKFLOW, SCRIPTS_README, MAKEFILE):
            build_self_test_root(root)
            (root / rel).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing required file did not abort: {rel}")

        for rel in SURFACE_PATHS:
            if rel in (WORKFLOW, SCRIPTS_README, MAKEFILE):
                continue
            build_self_test_root(root)
            (root / rel).unlink()
            assert ("MISSING_SURFACE_PATH", rel.as_posix()) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        for rel in ARCHIVE_SURFACE_PATHS:
            archive_path = root / rel
            if archive_path.exists():
                archive_path.unlink()
        assert (
            "MISSING_ARCHIVE_SURFACE",
            " or ".join(rel.as_posix() for rel in ARCHIVE_SURFACE_PATHS),
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root / ARCHIVE_SURFACE_PATHS[0], "present\n")
        assert collect_issues(root) == []
        checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_KBUILD_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_KBUILD_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KBUILD_ROUTES=pass")
    print(f"PHASE2_KBUILD_ROUTES_SURFACE_COUNT={len(SURFACE_PATHS) + 1}")
    print(f"PHASE2_KBUILD_ROUTES_README_MARKER_COUNT={len(README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
