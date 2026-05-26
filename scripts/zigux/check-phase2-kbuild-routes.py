#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 kbuild packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
VALIDATE_PHASE2 = ROOT / "scripts" / "zigux" / "validate-phase2.py"
VALIDATE_PHASE2_CLOSURE = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
THIRD_PARTY_ARCHIVE = ROOT / "third_party" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
THIRD_PARTY_ARCHIVE_PARTS_MANIFEST = (
    ROOT
    / "third_party"
    / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts"
    / "manifest.json"
)
ARCHIVE_SURFACE_PATHS = (
    THIRD_PARTY_ARCHIVE,
    THIRD_PARTY_ARCHIVE_PARTS_MANIFEST,
)
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py",
    ROOT / "scripts" / "zigux" / "stage-pinned-zig-archive.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-contract.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-selftest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-allconfig-helper-packet.py",
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "artifact_diff.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_ambiguous_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    PHASE2_CLOSURE,
    VALIDATE_PHASE2,
    VALIDATE_PHASE2_CLOSURE,
    THIRD_PARTY_README,
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    MAKEFILE,
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
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

README_REQUIRED_LINES = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the helper-local kconfig allconfig guard, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "- `scripts/zigux/kconfig/conf_bridge.zig` keeps the shipped sixteen-mode request-plan bridge explicit from the scripts root, including the `helpnewconfig` `silent` option handling and the same `randconfig`, `defconfig`, `savedefconfig`, and `syncconfig` argument surfaces that the Phase 2 wrapper-first roadmap tranche expects",
    "- `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the current conf-side and confdata-side bridge evidence packet explicit from the scripts root without pretending the broader closure packet is still directly readable",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, helper-local kconfig allconfig, and required-make-route guards that survive on current `master`",
    "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
    "- `third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the shipped Lane 05 local-first archive workflow, local archive README, archive-verification, and staged repo-local archive helper packet explicit from the scripts root beside that same pinned archive path",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "- keep those installer, helper-local kconfig allconfig guard, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    "- if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
)

README_WARNING_LINES = (
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
)

README_FORBIDDEN_MARKERS = (
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those installer and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, and `make -C zigux phase2`",
)

REQUIRED_MAKEFILE_LINES = (
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
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
)

DISALLOWED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/fixdep.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/genksyms.zig",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(README_REQUIRED_LINES)
    + len(README_REQUIRED_LINES)
    + len(README_WARNING_LINES)
    + len(README_WARNING_LINES)
    + len(README_FORBIDDEN_MARKERS)
    + 2
    + (len(SURFACE_PATHS) - 1)
    + 2
    + len(REQUIRED_MAKEFILE_LINES)
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

def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]

def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
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
    issues.extend(collect_exact_line_issues(readme_text, README_REQUIRED_LINES, "MISSING_README_REQUIRED_LINES", "DUPLICATE_README_REQUIRED_LINES"))
    issues.extend(collect_exact_line_issues(readme_text, README_WARNING_LINES, "MISSING_README_WARNING_LINES", "DUPLICATE_README_WARNING_LINES"))
    issues.extend(collect_forbidden_markers(readme_text, README_FORBIDDEN_MARKERS, "FORBIDDEN_README_MARKERS"))
    issues.extend(collect_exact_line_issues(makefile_text, REQUIRED_MAKEFILE_LINES, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES"))
    issues.extend(collect_forbidden_markers(makefile_text, DISALLOWED_MAKEFILE_LINES, "FORBIDDEN_MAKEFILE_LINES"))
    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))
    if not any(resolve_path(root, path).exists() for path in ARCHIVE_SURFACE_PATHS):
        issues.append(("MISSING_ARCHIVE_SURFACE_PATHS", " or ".join(path.relative_to(ROOT).as_posix() for path in ARCHIVE_SURFACE_PATHS)))
    return issues

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    readme_lines = ["# scripts/zigux", "", "## Phase 2", "", *README_REQUIRED_LINES, *README_WARNING_LINES]
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(("ZIG ?= zig", "ZIGUX_ROOT := ..", "", *REQUIRED_MAKEFILE_LINES)) + "\n")
    for path in SURFACE_PATHS:
        if path == MAKEFILE:
            continue
        write_text(resolve_path(root, path), "present\n")
    write_text(resolve_path(root, THIRD_PARTY_ARCHIVE_PARTS_MANIFEST), "present\n")

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

def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kbuild_routes_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            checks_run += 1
        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1
        for marker in README_REQUIRED_LINES:
            build_self_test_root(root)
            readme_path = resolve_path(root, SCRIPTS_README)
            readme_path.write_text(replace_exact_line(readme_path.read_text(encoding="utf-8"), marker, "BROKEN_PRESENT_MARKER"), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_README_REQUIRED_LINES", marker) in issues
            checks_run += 1
        for marker in README_REQUIRED_LINES:
            build_self_test_root(root)
            readme_path = resolve_path(root, SCRIPTS_README)
            readme_path.write_text(duplicate_exact_line(readme_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_README_REQUIRED_LINES", f"{marker}:count=2") in issues
            checks_run += 1
        for marker in README_WARNING_LINES:
            build_self_test_root(root)
            readme_path = resolve_path(root, SCRIPTS_README)
            readme_path.write_text(replace_exact_line(readme_path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_README_WARNING_LINES", marker) in issues
            checks_run += 1
        for marker in README_WARNING_LINES:
            build_self_test_root(root)
            readme_path = resolve_path(root, SCRIPTS_README)
            readme_path.write_text(duplicate_exact_line(readme_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_README_WARNING_LINES", f"{marker}:count=2") in issues
            checks_run += 1
        for marker in README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            readme_path = resolve_path(root, SCRIPTS_README)
            readme_path.write_text(readme_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_README_MARKERS", marker) in issues
            checks_run += 1
        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing makefile did not abort")
        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing workflow did not abort")
        for path in SURFACE_PATHS:
            if path == MAKEFILE:
                continue
            build_self_test_root(root)
            surface_path = resolve_path(root, path)
            surface_path.unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1
        build_self_test_root(root)
        resolve_path(root, THIRD_PARTY_ARCHIVE_PARTS_MANIFEST).unlink()
        write_text(resolve_path(root, THIRD_PARTY_ARCHIVE), "present\n")
        assert collect_issues(root) == []
        checks_run += 1
        build_self_test_root(root)
        archive_path = resolve_path(root, THIRD_PARTY_ARCHIVE)
        if archive_path.exists():
            archive_path.unlink()
        resolve_path(root, THIRD_PARTY_ARCHIVE_PARTS_MANIFEST).unlink()
        issues = collect_issues(root)
        assert ("MISSING_ARCHIVE_SURFACE_PATHS", " or ".join(path.relative_to(ROOT).as_posix() for path in ARCHIVE_SURFACE_PATHS)) in issues
        checks_run += 1
        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_LINES", marker) in issues
            checks_run += 1
        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in issues
            checks_run += 1
        for marker in DISALLOWED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(makefile_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MAKEFILE_LINES", marker) in issues
            checks_run += 1
    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
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
    print(f"PHASE2_KBUILD_ROUTES_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
