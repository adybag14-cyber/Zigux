#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) >= 4 else Path.cwd()

README_PATH = Path("scripts/zigux/README.md")
NOTES_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_PATH = Path("Documentation/zigux/phase2-closure.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = [
    README_PATH,
    NOTES_PATH,
    CLOSURE_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
]

README_REQUIRED_MARKERS = [
    "current scripts-root bridge packet stays reviewable",
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
]

README_FORBIDDEN_MARKERS = [
    "`check-phase2-kconfig-readme-alignment.py`",
    "`check-phase2-tool-manifest-packets.py`",
]

NOTES_REQUIRED_MARKERS = [
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
]

CLOSURE_REQUIRED_MARKERS = [
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
]

WORKFLOW_REQUIRED_MARKERS = [
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
]

MAKEFILE_REQUIRED_MARKERS = [
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
]

MANIFEST_REQUIRED_CHECKERS = [
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
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
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest object: {path}")
    return payload


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
    manifest = load_manifest(root / MANIFEST_PATH)

    for marker in README_REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"README_MISSING_MARKER={marker}")
    for marker in README_FORBIDDEN_MARKERS:
        if marker in readme_text:
            issues.append(f"README_FORBIDDEN_MARKER={marker}")
    for marker in NOTES_REQUIRED_MARKERS:
        if marker not in notes_text:
            issues.append(f"NOTES_MISSING_MARKER={marker}")
    for marker in CLOSURE_REQUIRED_MARKERS:
        if marker not in closure_text:
            issues.append(f"CLOSURE_MISSING_MARKER={marker}")
    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow_text:
            issues.append(f"WORKFLOW_MISSING_MARKER={marker}")
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            issues.append(f"MAKEFILE_MISSING_MARKER={marker}")

    checkers = manifest.get("present_surfaces", {})
    if not isinstance(checkers, dict):
        issues.append("MANIFEST_PRESENT_SURFACES_NOT_OBJECT")
        return issues
    manifest_checkers = checkers.get("checkers")
    if not isinstance(manifest_checkers, list):
        issues.append("MANIFEST_CHECKERS_NOT_LIST")
        return issues
    for checker in MANIFEST_REQUIRED_CHECKERS:
        if checker not in manifest_checkers:
            issues.append(f"MANIFEST_MISSING_CHECKER={checker}")

    return issues


def sample_root_contents() -> dict[Path, str]:
    return {
        README_PATH: """# scripts/zigux

## Phase 2

- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older rematerialized assumptions inside that now-rematerialized toolchain packet
- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`
- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording
- keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet
""",
        NOTES_PATH: """# Phase 2 Toolchain Bootstrap Notes

- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` are current shipped guards
- `.github/workflows/zigux-bootstrap.yml` runs `python3 scripts/zigux/check-zig-toolchain.py --policy-only` and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- the make-wrapper packet keeps `make -C zigux phase2-genksyms` and `make -C zigux phase2-fixdep` explicit beside the returned scripts-root packet
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
""",
        WORKFLOW_PATH: """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - run: python3 scripts/zigux/check-zig-toolchain.py --self-test
      - run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
      - run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test
      - run: python3 scripts/zigux/check-phase2-kbuild-routes.py
      - run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test
      - run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py
      - run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test
      - run: python3 scripts/zigux/check-phase2-required-make-routes.py
      - run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test
      - run: python3 scripts/zigux/check-phase2-tool-manifest.py
      - run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test
      - run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py
      - run: zig test scripts/zigux/genksyms.zig
      - run: zig test scripts/zigux/fixdep.zig
      - run: make -C zigux phase2-genksyms
      - run: make -C zigux phase2-fixdep
""",
        MAKEFILE_PATH: """phase2-toolchain:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing

phase2-tools:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py

phase2-genksyms:
\tzig test scripts/zigux/genksyms.zig

phase2-fixdep:
\tzig test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
""",
        MANIFEST_PATH: json.dumps(
            {
                "present_surfaces": {
                    "checkers": MANIFEST_REQUIRED_CHECKERS,
                }
            },
            indent=2,
        )
        + "\n",
    }


def write_sample_root(root: Path) -> None:
    for rel_path, text in sample_root_contents().items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_root_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert validate_root(root) == []
        checks_run += 1

        (root / README_PATH).write_text(read_text(root / README_PATH).replace("check-phase2-required-make-routes.py", "", 1), encoding="utf-8")
        issues = validate_root(root)
        assert any(issue.startswith("README_MISSING_MARKER=") for issue in issues)
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_root_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        (root / README_PATH).write_text(read_text(root / README_PATH) + "\n`check-phase2-tool-manifest-packets.py`\n", encoding="utf-8")
        issues = validate_root(root)
        assert "README_FORBIDDEN_MARKER=`check-phase2-tool-manifest-packets.py`" in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_root_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        (root / WORKFLOW_PATH).unlink()
        issues = validate_root(root)
        assert "MISSING_FILE=.github/workflows/zigux-bootstrap.yml" in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_root_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        manifest = load_manifest(root / MANIFEST_PATH)
        checkers = manifest["present_surfaces"]["checkers"]
        checkers.remove("scripts/zigux/check-phase2-artifact-tools-manifest.py")
        (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert "MANIFEST_MISSING_CHECKER=scripts/zigux/check-phase2-artifact-tools-manifest.py" in issues
        checks_run += 1

    print("PHASE2_SCRIPTS_ROOT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_ROOT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 2 scripts-root packet stays aligned with its live companion surfaces."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to validate")
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
        print("PHASE2_SCRIPTS_ROOT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_SCRIPTS_ROOT_PACKET=pass")
    print(f"PHASE2_SCRIPTS_ROOT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_SCRIPTS_ROOT_PACKET_README_MARKER_COUNT={len(README_REQUIRED_MARKERS)}")
    print(f"PHASE2_SCRIPTS_ROOT_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(f"PHASE2_SCRIPTS_ROOT_PACKET_MANIFEST_CHECKER_COUNT={len(MANIFEST_REQUIRED_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
