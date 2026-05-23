#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain make-wrapper packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
SCRIPTS_README = Path("scripts/zigux/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_README = Path("third_party/README.md")

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
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
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
)

README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    ".github/workflows/zigux-bootstrap.yml",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
)

MANIFEST_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

MANIFEST_SURFACES = {
    "bootstrap_helpers": (
        "scripts/zigux/install-zig.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
    ),
    "checkers": (
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "scripts/zigux/check-lane05-stage-helper-contract.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    ),
    "archive_support": (
        "third_party/README.md",
        "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
    ),
    "policy": (
        "scripts/zigux/zig-toolchain-policy.json",
    ),
}

REQUIRED_FILE_SURFACES = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve(root: Path, relative: Path | str) -> Path:
    rel = Path(relative)
    return root / rel


def count_exact_lines(text: str, marker: str) -> int:
    accepted = {marker, f"- {marker}"}
    return sum(1 for line in text.splitlines() if line.strip() in accepted)


def require_exact_lines(issues: list[tuple[str, str]], text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> None:
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    readme_text = read_text(resolve(root, SCRIPTS_README))
    policy = json.loads(read_text(resolve(root, POLICY)))
    manifest = json.loads(read_text(resolve(root, TOOL_MANIFEST)))

    require_exact_lines(issues, workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE")
    require_exact_lines(issues, makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE")

    for marker in README_MARKERS:
        if marker not in readme_text:
            issues.append(("MISSING_README_MARKER", marker))

    for key, value in MANIFEST_TOP_LEVEL.items():
        if manifest.get(key) != value:
            issues.append(("MISMATCH_MANIFEST_TOP_LEVEL", f"{key}={manifest.get(key)!r}"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_PRESENT_SURFACES", "present_surfaces"))
        return issues

    for bucket, markers in MANIFEST_SURFACES.items():
        values = present_surfaces.get(bucket)
        if not isinstance(values, list):
            issues.append(("INVALID_MANIFEST_BUCKET", bucket))
            continue
        for marker in markers:
            if marker not in values:
                issues.append(("MISSING_MANIFEST_MARKER", f"{bucket}:{marker}"))

    required_routes = policy.get("upgrade_policy", {}).get("required_make_routes")
    if required_routes != ["phase2-toolchain", "phase2-validate", "phase2-cross"]:
        issues.append(("MISMATCH_REQUIRED_MAKE_ROUTES", repr(required_routes)))

    archive_scope = policy.get("upgrade_policy", {}).get("archive_target_scope")
    if archive_scope != ["x86_64-linux"]:
        issues.append(("MISMATCH_ARCHIVE_TARGET_SCOPE", repr(archive_scope)))

    for relative in REQUIRED_FILE_SURFACES:
        if not resolve(root, relative).exists():
            issues.append(("MISSING_REQUIRED_FILE", relative))
    if not resolve(root, THIRD_PARTY_README).exists():
        issues.append(("MISSING_REQUIRED_FILE", str(THIRD_PARTY_README)))

    return issues


def format_issue(code: str, detail: str) -> str:
    return f"{code}: {detail}"


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
    ]
    workflow_lines.extend(f"      - {line}" for line in WORKFLOW_LINES)
    write_text(resolve(root, WORKFLOW), "\n".join(workflow_lines) + "\n")

    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        ".PHONY: phase2-toolchain phase2-validate phase2-cross",
    ]
    makefile_lines.extend(MAKEFILE_LINES)
    write_text(resolve(root, MAKEFILE), "\n".join(makefile_lines) + "\n")

    readme_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "- " + ", ".join(README_MARKERS[:3]) + " remain the shipped Phase 2 toolchain guards.",
        "- " + ", ".join(README_MARKERS[3:7]) + " keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path.",
        "- " + ", ".join(README_MARKERS[7:]) + " keep the shipped helper and make-wrapper packet explicit from the scripts root.",
    ]
    write_text(resolve(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")

    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": {bucket: list(markers) for bucket, markers in MANIFEST_SURFACES.items()},
    }
    write_text(resolve(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")

    policy = {
        "channel": "0.17.0-dev.87+9b177a7d2",
        "upgrade_policy": {
            "archive_target_scope": ["x86_64-linux"],
            "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
        },
    }
    write_text(resolve(root, POLICY), json.dumps(policy, indent=2) + "\n")

    write_text(resolve(root, THIRD_PARTY_README), "# third_party\n")
    for relative in REQUIRED_FILE_SURFACES:
        write_text(resolve(root, relative), "placeholder\n")


def expect_ok(name: str, issues: list[tuple[str, str]]) -> None:
    if issues:
        rendered = "; ".join(format_issue(code, detail) for code, detail in issues)
        raise AssertionError(f"{name} unexpectedly failed: {rendered}")


def expect_issue(name: str, issues: list[tuple[str, str]], code: str, detail_fragment: str) -> None:
    for issue_code, issue_detail in issues:
        if issue_code == code and detail_fragment in issue_detail:
            return
    rendered = "; ".join(format_issue(issue_code, issue_detail) for issue_code, issue_detail in issues)
    raise AssertionError(f"{name} missing expected issue {code}:{detail_fragment}; got {rendered}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_make_wrapper_") as tmp:
        root = Path(tmp)
        build_sample_root(root)

        cases = 0

        expect_ok("sample_root", collect_issues(root))
        cases += 1

        workflow_path = resolve(root, WORKFLOW)
        original_workflow = read_text(workflow_path)
        write_text(workflow_path, original_workflow.replace(WORKFLOW_LINES[0] + "\n", "", 1))
        expect_issue("missing_workflow_line", collect_issues(root), "MISSING_WORKFLOW_LINE", WORKFLOW_LINES[0])
        cases += 1
        build_sample_root(root)

        write_text(workflow_path, read_text(workflow_path) + f"      - {WORKFLOW_LINES[0]}\n")
        expect_issue("duplicate_workflow_line", collect_issues(root), "DUPLICATE_WORKFLOW_LINE", WORKFLOW_LINES[0])
        cases += 1
        build_sample_root(root)

        makefile_path = resolve(root, MAKEFILE)
        original_makefile = read_text(makefile_path)
        write_text(makefile_path, original_makefile.replace(MAKEFILE_LINES[-1] + "\n", "", 1))
        expect_issue("missing_makefile_line", collect_issues(root), "MISSING_MAKEFILE_LINE", MAKEFILE_LINES[-1])
        cases += 1
        build_sample_root(root)

        readme_path = resolve(root, SCRIPTS_README)
        original_readme = read_text(readme_path)
        write_text(readme_path, original_readme.replace(README_MARKERS[-1], "phase2-toolchain-missing"))
        expect_issue("missing_readme_marker", collect_issues(root), "MISSING_README_MARKER", README_MARKERS[-1])
        cases += 1
        build_sample_root(root)

        manifest_path = resolve(root, TOOL_MANIFEST)
        manifest = json.loads(read_text(manifest_path))
        manifest["present_surfaces"]["bootstrap_helpers"].remove("scripts/zigux/stage-pinned-zig-archive.py")
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_issue("missing_manifest_marker", collect_issues(root), "MISSING_MANIFEST_MARKER", "bootstrap_helpers:scripts/zigux/stage-pinned-zig-archive.py")
        cases += 1
        build_sample_root(root)

        policy_path = resolve(root, POLICY)
        policy = json.loads(read_text(policy_path))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        write_text(policy_path, json.dumps(policy, indent=2) + "\n")
        expect_issue("mismatch_required_routes", collect_issues(root), "MISMATCH_REQUIRED_MAKE_ROUTES", "phase2-cross")
        cases += 1
        build_sample_root(root)

        helper_path = resolve(root, "scripts/zigux/stage-pinned-zig-archive.py")
        helper_path.unlink()
        expect_issue("missing_required_file", collect_issues(root), "MISSING_REQUIRED_FILE", "scripts/zigux/stage-pinned-zig-archive.py")
        cases += 1

        print("PHASE2_TOOLCHAIN_MAKE_WRAPPER_SELF_TEST=pass")
        print(f"PHASE2_TOOLCHAIN_MAKE_WRAPPER_SELF_TEST_CASE_COUNT={cases}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in coverage")
    parser.add_argument("--write-sample-root", type=Path, help="write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return

    issues = collect_issues(args.root)
    if issues:
        for code, detail in issues:
            print(format_issue(code, detail))
        raise SystemExit(1)

    print("PHASE2_TOOLCHAIN_MAKE_WRAPPER=pass")
    print(f"PHASE2_TOOLCHAIN_MAKE_WRAPPER_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_MAKE_WRAPPER_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_MAKE_WRAPPER_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_MAKE_WRAPPER_MANIFEST_BUCKET_COUNT={len(MANIFEST_SURFACES)}")


if __name__ == "__main__":
    main()
