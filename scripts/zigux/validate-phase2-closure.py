#!/usr/bin/env python3
"""Validate the current Phase 2 closure-side packet against live repo surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_EXISTING_PATHS = (
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-lane05-install-zig-archive-verification.py"),
    Path("scripts/zigux/check-lane05-stage-helper-contract.py"),
    Path("scripts/zigux/check-lane05-stage-helper-selftest.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/stage-pinned-zig-archive.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"),
    Path("scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"),
    Path("scripts/zigux/fixdep.zig"),
    Path("third_party/README.md"),
    Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"),
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

EXPECTED_MANIFEST_SURFACES = {
    "archive_support": (
        "third_party/README.md",
        "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    ),
    "artifact_support": (
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "bootstrap_helpers": (
        "scripts/zigux/install-zig.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
    ),
    "bridge_helpers": (
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    ),
    "checkers": (
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "scripts/zigux/check-lane05-stage-helper-contract.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/check-phase2-kbuild-routes.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
    ),
    "closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ),
}


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


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_manifest_list(
    issues: list[tuple[str, str]],
    manifest: dict[str, object],
    key: str,
) -> list[str] | None:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(
    issues: list[tuple[str, str]],
    label: str,
    actual: list[str] | None,
    expected: tuple[str, ...],
) -> None:
    if actual is None:
        return
    for item in expected:
        if item not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{item}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_EXISTING_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))

    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    closure_text = read_text(resolve(root, CLOSURE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    for key, expected in EXPECTED_MANIFEST_SURFACES.items():
        expect_subset(issues, key, require_manifest_list(issues, manifest, key), expected)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_lines = [
        "# Phase 2 Closure",
        "",
        *[f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS],
        "",
    ]
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        "ZIG ?= zig",
        "",
        *REQUIRED_MAKEFILE_LINES,
    ]
    manifest = {
        "phase": "Phase 2",
        "repo_reality_gaps": [],
        "present_surfaces": {
            key: list(expected) for key, expected in EXPECTED_MANIFEST_SURFACES.items()
        },
    }

    write_text(resolve(root, CLOSURE_REL), "\n".join(closure_lines))
    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, MAKEFILE_REL), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")

    for rel in REQUIRED_EXISTING_PATHS:
        path = resolve(root, rel)
        if rel.suffix == ".json":
            write_text(path, "{}\n")
        else:
            write_text(path, "present\n")


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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve(root, CLOSURE_REL)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
                "run: python3 scripts/zigux/other.py",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve(root, MAKEFILE_REL)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
                "# removed",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove(
            "scripts/zigux/check-lane05-install-zig-archive-verification.py"
        )
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "checkers:scripts/zigux/check-lane05-install-zig-archive-verification.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bootstrap_helpers"].remove(
            "scripts/zigux/stage-pinned-zig-archive.py"
        )
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "bootstrap_helpers:scripts/zigux/stage-pinned-zig-archive.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = ["docs drift"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_MANIFEST_GAPS", "['docs drift']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (resolve(root, REQUIRED_EXISTING_PATHS[0])).unlink()
        assert (
            "MISSING_REQUIRED_FILE",
            REQUIRED_EXISTING_PATHS[0].as_posix(),
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 2 closure note against the shipped closure packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_PACKET=archive_stage_tool_manifest_make_routes")
    print("PHASE2_CLOSURE_STATUS=parked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
