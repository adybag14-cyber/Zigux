#!/usr/bin/env python3
"""Guard the current Lane 18 Phase 2 scripts-root and action-path packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

README_PATH = Path("scripts/zigux/README.md")
NOTES_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_PATH = Path("Documentation/zigux/phase2-closure.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    README_PATH,
    NOTES_PATH,
    CLOSURE_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    MANIFEST_PATH,
)

README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

MANIFEST_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
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
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def check_markers(text: str, markers: tuple[str, ...], code: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{code}={marker}")


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"MISSING_FILE={rel_path.as_posix()}")
    if issues:
        return issues

    readme_text = read_text(root / README_PATH)
    notes_text = read_text(root / NOTES_PATH)
    closure_text = read_text(root / CLOSURE_PATH)
    workflow_text = read_text(root / WORKFLOW_PATH)
    makefile_text = read_text(root / MAKEFILE_PATH)
    manifest = json.loads(read_text(root / MANIFEST_PATH))

    check_markers(readme_text, README_MARKERS, "README_MISSING_MARKER", issues)
    check_markers(notes_text, NOTES_MARKERS, "NOTES_MISSING_MARKER", issues)
    check_markers(closure_text, CLOSURE_MARKERS, "CLOSURE_MISSING_MARKER", issues)
    check_markers(workflow_text, WORKFLOW_LINES, "WORKFLOW_MISSING_MARKER", issues)
    check_markers(makefile_text, MAKEFILE_MARKERS, "MAKEFILE_MISSING_MARKER", issues)

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append("MANIFEST_PRESENT_SURFACES_NOT_OBJECT")
        return issues
    manifest_checkers = present_surfaces.get("checkers")
    if not isinstance(manifest_checkers, list):
        issues.append("MANIFEST_CHECKERS_NOT_LIST")
        return issues
    for checker in MANIFEST_CHECKERS:
        if checker not in manifest_checkers:
            issues.append(f"MANIFEST_MISSING_CHECKER={checker}")

    return issues


def sample_root_contents() -> dict[Path, str]:
    manifest = {
        "present_surfaces": {
            "checkers": list(MANIFEST_CHECKERS),
        }
    }
    return {
        README_PATH: """# scripts/zigux

## Phase 2

- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, the restored closure-side validator packet, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older rematerialized assumptions inside that now-rematerialized toolchain packet
- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-required-make-routes.py`
- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks
- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording
""",
        NOTES_PATH: """# Phase 2 Toolchain Bootstrap Notes

- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py` are current shipped guards
- `.github/workflows/zigux-bootstrap.yml` runs `python3 scripts/zigux/check-zig-toolchain.py --policy-only` and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- the make-wrapper packet keeps `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, and `make -C zigux phase2-validate` explicit beside the returned scripts-root packet
""",
        CLOSURE_PATH: """# Phase 2 Closure

- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-zig-toolchain.py`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
""",
        WORKFLOW_PATH: "\n".join(f"- {line}" if line.startswith("run:") else line for line in WORKFLOW_LINES) + "\n",
        MAKEFILE_PATH: """phase2-toolchain:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing

phase2-tools:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py

phase2-cross:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-genksyms:
\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig

phase2-fixdep:
\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py
""",
        MANIFEST_PATH: json.dumps(manifest, indent=2) + "\n",
    }


def write_sample_root(root: Path) -> None:
    for rel_path, content in sample_root_contents().items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert validate_root(root) == []
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        (root / README_PATH).write_text(read_text(root / README_PATH).replace("`scripts/zigux/check-phase2-required-make-routes.py`", "", 1), encoding="utf-8")
        issues = validate_root(root)
        assert any(issue.startswith("README_MISSING_MARKER=") for issue in issues)
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        workflow = read_text(root / WORKFLOW_PATH)
        (root / WORKFLOW_PATH).write_text(workflow.replace("run: make -C zigux phase2-fixdep", "run: make -C zigux phase2-other", 1), encoding="utf-8")
        issues = validate_root(root)
        assert "WORKFLOW_MISSING_MARKER=run: make -C zigux phase2-fixdep" in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        (root / MAKEFILE_PATH).unlink()
        issues = validate_root(root)
        assert f"MISSING_FILE={MAKEFILE_PATH.as_posix()}" in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-tool-manifest.py")
        (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert "MANIFEST_MISSING_CHECKER=scripts/zigux/check-phase2-tool-manifest.py" in issues
        checks_run += 1

    print("PHASE2_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CURRENT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Lane 18 Phase 2 scripts-root and action-path packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic coverage")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    issues = validate_root(args.root)
    if issues:
        print("PHASE2_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CURRENT_PACKET=pass")
    print(f"PHASE2_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_CURRENT_PACKET_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_CURRENT_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CURRENT_PACKET_MANIFEST_CHECKER_COUNT={len(MANIFEST_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
