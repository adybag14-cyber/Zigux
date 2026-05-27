#!/usr/bin/env python3
"""Guard the rematerialized Phase 2 make-wrapper packet and toolchain lane boundary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)

REQUIRED_PHASE2_PHONY_LINE = ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"
REQUIRED_PHASE2_PHONY_TARGETS = tuple(REQUIRED_PHASE2_PHONY_LINE.split(":", 1)[1].strip().split())
CURRENT_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
CURRENT_REQUIRED_MAKE_ROUTE_SET = frozenset(CURRENT_REQUIRED_MAKE_ROUTES)
CURRENT_POLICY_ROUTE_MARKERS = tuple(f"`make -C zigux {route}`" for route in CURRENT_REQUIRED_MAKE_ROUTES)
CURRENT_WORKFLOW_ROUTE_LINES = tuple(f"run: make -C zigux {route}" for route in CURRENT_REQUIRED_MAKE_ROUTES)
POLICY_SUMMARY_ANCHOR = "required Linux-style make routes"
TOOLCHAIN_ROUTE = "phase2-toolchain"
TOOLCHAIN_ALLOWED_RECIPE_LINES = (
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
)
TOOLCHAIN_OVERLAP_FRAGMENTS = (
    "check-phase2-kbuild-routes.py",
    "check-phase2-docs-shared-reminder.py",
    "check-phase2-required-make-routes.py",
    "check-phase2-artifact-tools-manifest.py",
    "check-kconfig-bridge.py",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-kconfig-allconfig-helper-packet.py",
    "check-phase2-cross.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-genksyms-bridge.py",
    "check-phase2-genksyms-selftest-alignment.py",
    "genksyms.zig",
    "check-phase2-fixdep-gate.py",
    "check-fixdep-diff.py",
    "fixdep.zig",
    "make -C zigux phase2-",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "phase2: phase2-validate",
)

CURRENT_PACKET_ROUTE_MARKERS = (
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

MINIMAL_SURFACE_MARKERS = ("`zigux/Makefile`",)

FULL_ROUTE_SURFACE_CODES = (
    (DOCS_README, "MISSING_DOCS_README_MARKERS", "MISSING_DOCS_README_ROUTE_MARKERS"),
    (BOOTSTRAP_NOTES, "MISSING_BOOTSTRAP_GAP_MARKERS", "MISSING_BOOTSTRAP_ROUTE_MARKERS"),
    (REVIEW_CHECKLIST, "MISSING_REVIEW_GAP_MARKERS", "MISSING_REVIEW_ROUTE_MARKERS"),
    (SCRIPTS_README, "MISSING_SCRIPTS_README_GAP_MARKERS", "MISSING_SCRIPTS_README_ROUTE_MARKERS"),
)

POLICY_ROUTE_SURFACE_CODES = (
    (TESTS_README, "MISSING_TESTS_GAP_MARKERS", "MISSING_TESTS_ROUTE_MARKERS"),
)

POLICY_SUMMARY_SURFACE_CODES = (
    (BOOTSTRAP_NOTES, "MISSING_BOOTSTRAP_POLICY_ROUTE_SUMMARY", "MISSING_BOOTSTRAP_POLICY_ROUTE_NAME"),
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(CURRENT_WORKFLOW_ROUTE_LINES)
    + len(CURRENT_WORKFLOW_ROUTE_LINES)
    + 1
    + len(MAKEFILE_MARKERS)
    + len(MAKEFILE_MARKERS)
    + 1
    + (len(MINIMAL_SURFACE_MARKERS) + len(CURRENT_PACKET_ROUTE_MARKERS)) * len(FULL_ROUTE_SURFACE_CODES)
    + (len(MINIMAL_SURFACE_MARKERS) + len(CURRENT_POLICY_ROUTE_MARKERS)) * len(POLICY_ROUTE_SURFACE_CODES)
    + 1
    + len(CURRENT_REQUIRED_MAKE_ROUTES)
    + 1
    + 10
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def has_required_phase2_phony_targets(text: str) -> bool:
    return set(REQUIRED_PHASE2_PHONY_TARGETS).issubset(phony_targets_present(text))


def load_required_make_routes(policy_path: Path) -> list[str]:
    payload = json.loads(read_text(policy_path))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes in {policy_path}")
        normalized_route = route.strip()
        if normalized_route in seen:
            raise ValueError(f"duplicate required_make_routes in {policy_path}: {normalized_route}")
        seen.add(normalized_route)
        normalized.append(normalized_route)
    return normalized


def format_route_marker(route: str) -> str:
    return f"`make -C zigux {route}`"


def format_workflow_route_line(route: str) -> str:
    return f"run: make -C zigux {route}"


def format_makefile_target_line(route: str) -> str:
    return f"{route}:"


def count_target_definitions(text: str, route: str) -> int:
    prefix = format_makefile_target_line(route)
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def collect_target_recipe_lines(text: str, route: str) -> list[str]:
    target_prefix = format_makefile_target_line(route)
    collecting = False
    recipe_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not collecting:
            if stripped.startswith(target_prefix):
                collecting = True
            continue
        if stripped and not line.startswith((" ", "\t")):
            break
        if line.startswith((" ", "\t")):
            recipe_lines.append(stripped)
    return recipe_lines


def format_policy_summary_line(routes: tuple[str, ...] | list[str]) -> str:
    joined = ", ".join(routes)
    return f"policy note keeps {joined} as {POLICY_SUMMARY_ANCHOR} when those routes are rematerialized."


def collect_surface_issues(
    root: Path,
    path: Path,
    gap_code: str,
    route_code: str,
    route_markers: tuple[str, ...],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = read_text(resolve_path(root, path))
    for marker in MINIMAL_SURFACE_MARKERS:
        if marker not in text:
            issues.append((gap_code, marker))
    for marker in route_markers:
        if marker not in text:
            issues.append((route_code, marker))
    return issues


def collect_policy_summary_issues(
    root: Path,
    path: Path,
    summary_code: str,
    route_code: str,
    required_routes: tuple[str, ...],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = read_text(resolve_path(root, path))
    summary_lines = [line.strip() for line in text.splitlines() if POLICY_SUMMARY_ANCHOR in line]
    if not summary_lines:
        issues.append((summary_code, POLICY_SUMMARY_ANCHOR))
        return issues

    summary_text = "\n".join(summary_lines)
    for route in required_routes:
        if route not in summary_text:
            issues.append((route_code, route))
    return issues


def collect_required_route_makefile_issues(
    makefile_text: str,
    required_routes: tuple[str, ...],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    phony_targets = phony_targets_present(makefile_text)
    for route in required_routes:
        if route not in phony_targets:
            issues.append(("MISSING_REQUIRED_ROUTE_PHONY_TARGET", route))

        target_line = format_makefile_target_line(route)
        count = count_target_definitions(makefile_text, route)
        if count == 0:
            issues.append(("MISSING_REQUIRED_ROUTE_TARGET", target_line))
        elif count != 1:
            issues.append(("DUPLICATE_REQUIRED_ROUTE_TARGET", f"{target_line}:count={count}"))
    return issues


def collect_toolchain_route_boundary_issues(makefile_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    recipe_lines = collect_target_recipe_lines(makefile_text, TOOLCHAIN_ROUTE)
    if not recipe_lines:
        return issues

    for marker in TOOLCHAIN_ALLOWED_RECIPE_LINES:
        count = recipe_lines.count(marker)
        if count == 0:
            issues.append(("MISSING_TOOLCHAIN_ROUTE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_TOOLCHAIN_ROUTE_LINE", f"{marker}:count={count}"))

    for recipe_line in recipe_lines:
        for fragment in TOOLCHAIN_OVERLAP_FRAGMENTS:
            if fragment in recipe_line:
                issues.append(("TOOLCHAIN_ROUTE_OVERLAP", recipe_line))
                break

    return issues


def collect_route_packet_issues(required_routes: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for route in required_routes:
        if route not in CURRENT_REQUIRED_MAKE_ROUTE_SET:
            issues.append(("UNSUPPORTED_REQUIRED_ROUTE", route))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    required_routes = tuple(load_required_make_routes(resolve_path(root, TOOLCHAIN_POLICY)))
    policy_route_markers = tuple(format_route_marker(route) for route in required_routes)
    workflow_route_lines = tuple(format_workflow_route_line(route) for route in required_routes)

    issues.extend(collect_route_packet_issues(required_routes))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for line in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINES", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINES", f"{line}:count={count}"))
    for line in workflow_route_lines:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_ROUTE_LINES", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_ROUTE_LINES", f"{line}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    if not has_required_phase2_phony_targets(makefile_text):
        issues.append(("MISSING_MAKEFILE_MARKERS", REQUIRED_PHASE2_PHONY_LINE))
    for marker in MAKEFILE_MARKERS:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count={count}"))
    issues.extend(collect_required_route_makefile_issues(makefile_text, required_routes))
    issues.extend(collect_toolchain_route_boundary_issues(makefile_text))

    for path, gap_code, route_code in FULL_ROUTE_SURFACE_CODES:
        issues.extend(collect_surface_issues(root, path, gap_code, route_code, CURRENT_PACKET_ROUTE_MARKERS))

    for path, gap_code, route_code in POLICY_ROUTE_SURFACE_CODES:
        issues.extend(collect_surface_issues(root, path, gap_code, route_code, policy_route_markers))

    for path, summary_code, route_code in POLICY_SUMMARY_SURFACE_CODES:
        issues.extend(collect_policy_summary_issues(root, path, summary_code, route_code, required_routes))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(CURRENT_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES + CURRENT_WORKFLOW_ROUTE_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join((REQUIRED_PHASE2_PHONY_LINE,) + MAKEFILE_MARKERS) + "\n")

    full_marker_text = "\n".join(MINIMAL_SURFACE_MARKERS + CURRENT_PACKET_ROUTE_MARKERS)
    for path, _, _ in FULL_ROUTE_SURFACE_CODES:
        write_text(resolve_path(root, path), full_marker_text + "\n")

    bootstrap_text = "\n".join(
        MINIMAL_SURFACE_MARKERS
        + CURRENT_PACKET_ROUTE_MARKERS
        + (format_policy_summary_line(CURRENT_REQUIRED_MAKE_ROUTES),)
    )
    write_text(resolve_path(root, BOOTSTRAP_NOTES), bootstrap_text + "\n")

    tests_marker_text = "\n".join(MINIMAL_SURFACE_MARKERS + CURRENT_POLICY_ROUTE_MARKERS)
    for path, _, _ in POLICY_ROUTE_SURFACE_CODES:
        write_text(resolve_path(root, path), tests_marker_text + "\n")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def insert_after_exact_line(text: str, marker: str, addition: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, addition)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_cli(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def assert_invalid_cli(root: Path, note_fragment: str | None = None) -> None:
    result = run_cli(root)
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    makefile_path = resolve_path(root, MAKEFILE)
    assert result.returncode == 1
    assert "PHASE2_REQUIRED_MAKE_ROUTES=invalid" in result.stdout
    assert f"PHASE2_REQUIRED_POLICY_PATH={policy_path}" in result.stdout
    assert f"PHASE2_REQUIRED_MAKEFILE_PATH={makefile_path}" in result.stdout
    assert "PHASE2_REQUIRED_MAKE_ROUTES_NOTE=" in result.stdout
    if note_fragment is not None:
        assert note_fragment in result.stdout


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_required_make_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), line),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINES", line) in collect_issues(root)
            checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), line),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINES", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        for line in CURRENT_WORKFLOW_ROUTE_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), line),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_ROUTE_LINES", line) in collect_issues(root)
            checks_run += 1

        for line in CURRENT_WORKFLOW_ROUTE_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), line),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_ROUTE_LINES", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_PHASE2_PHONY_LINE),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_MARKERS", REQUIRED_PHASE2_PHONY_LINE) in collect_issues(root)
        checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for path, gap_code, route_code in FULL_ROUTE_SURFACE_CODES:
            for marker in MINIMAL_SURFACE_MARKERS + CURRENT_PACKET_ROUTE_MARKERS:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    replace_once(resolved.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                if marker in MINIMAL_SURFACE_MARKERS:
                    assert (gap_code, marker) in issues
                else:
                    assert (route_code, marker) in issues
                checks_run += 1

        for path, gap_code, route_code in POLICY_ROUTE_SURFACE_CODES:
            for marker in MINIMAL_SURFACE_MARKERS + CURRENT_POLICY_ROUTE_MARKERS:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    replace_once(resolved.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                if marker in MINIMAL_SURFACE_MARKERS:
                    assert (gap_code, marker) in issues
                else:
                    assert (route_code, marker) in issues
                checks_run += 1

        build_self_test_root(root)
        bootstrap_path = resolve_path(root, BOOTSTRAP_NOTES)
        bootstrap_path.write_text(
            replace_once(bootstrap_path.read_text(encoding="utf-8"), POLICY_SUMMARY_ANCHOR),
            encoding="utf-8",
        )
        assert ("MISSING_BOOTSTRAP_POLICY_ROUTE_SUMMARY", POLICY_SUMMARY_ANCHOR) in collect_issues(root)
        checks_run += 1

        for route in CURRENT_REQUIRED_MAKE_ROUTES:
            build_self_test_root(root)
            bootstrap_path = resolve_path(root, BOOTSTRAP_NOTES)
            summary_line = format_policy_summary_line(CURRENT_REQUIRED_MAKE_ROUTES)
            bootstrap_path.write_text(
                replace_exact_line(
                    bootstrap_path.read_text(encoding="utf-8"),
                    summary_line,
                    summary_line.replace(route, "phase2-other", 1),
                ),
                encoding="utf-8",
            )
            assert ("MISSING_BOOTSTRAP_POLICY_ROUTE_NAME", route) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        extra_route = "phase2-future"
        policy_payload["upgrade_policy"]["required_make_routes"].append(extra_route)
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNSUPPORTED_REQUIRED_ROUTE", extra_route) in issues
        assert ("MISSING_TESTS_ROUTE_MARKERS", f"`make -C zigux {extra_route}`") in issues
        assert ("MISSING_WORKFLOW_ROUTE_LINES", f"run: make -C zigux {extra_route}") in issues
        assert ("MISSING_BOOTSTRAP_POLICY_ROUTE_NAME", extra_route) in issues
        assert ("MISSING_REQUIRED_ROUTE_PHONY_TARGET", extra_route) in issues
        assert ("MISSING_REQUIRED_ROUTE_TARGET", f"{extra_route}:") in issues
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        extra_route = "phase2-future"
        policy_payload["upgrade_policy"]["required_make_routes"].append(extra_route)
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + f"{extra_route}:\n\t@true\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("UNSUPPORTED_REQUIRED_ROUTE", extra_route) in issues
        assert ("MISSING_REQUIRED_ROUTE_PHONY_TARGET", extra_route) in issues
        assert ("MISSING_REQUIRED_ROUTE_TARGET", f"{extra_route}:") not in issues
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        extra_route = "phase2-future"
        policy_payload["upgrade_policy"]["required_make_routes"].append(extra_route)
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_text = replace_exact_line(
            makefile_text,
            REQUIRED_PHASE2_PHONY_LINE,
            REQUIRED_PHASE2_PHONY_LINE + f" {extra_route}",
        )
        makefile_text += f"{extra_route}:\n\t@true\n{extra_route}:\n\t@true\n"
        makefile_path.write_text(makefile_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNSUPPORTED_REQUIRED_ROUTE", extra_route) in issues
        assert ("DUPLICATE_REQUIRED_ROUTE_TARGET", f"{extra_route}::count=2") in issues
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        assert_invalid_cli(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"] = "broken"
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        assert_invalid_cli(root, "invalid upgrade_policy")
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["required_make_routes"] = []
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        assert_invalid_cli(root, "invalid required_make_routes")
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", " "]
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        assert_invalid_cli(root, "invalid required_make_routes")
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-toolchain"]
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        assert_invalid_cli(root, "duplicate required_make_routes")
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-future"]
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        result = run_cli(root)
        assert result.returncode == 1
        assert "PHASE2_REQUIRED_MAKE_ROUTES=fail" in result.stdout
        assert "UNSUPPORTED_REQUIRED_ROUTE:phase2-future" in result.stdout
        checks_run += 1

        for path in (TOOLCHAIN_POLICY, WORKFLOW, MAKEFILE):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the rematerialized Phase 2 make-wrapper packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        required_routes = load_required_make_routes(policy_path)
    except (ValueError, json.JSONDecodeError) as exc:
        print("PHASE2_REQUIRED_MAKE_ROUTES=invalid")
        print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
        print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
        print(f"PHASE2_REQUIRED_MAKE_ROUTES_NOTE={exc}")
        return 1

    issues = collect_issues(root)
    if issues:
        print("PHASE2_REQUIRED_MAKE_ROUTES=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_REQUIRED_MAKE_ROUTES=pass")
    print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    print(f"PHASE2_CURRENT_PACKET_ROUTE_COUNT={len(CURRENT_PACKET_ROUTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_ROUTE_RECIPE_COUNT={len(TOOLCHAIN_ALLOWED_RECIPE_LINES)}")
    print("PHASE2_TOOLCHAIN_ROUTE_BOUNDARY=bounded")
    print("PHASE2_REQUIRED_ROUTE_STATUS=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
