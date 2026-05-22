#!/usr/bin/env python3
"""Guard the current Phase 2 review-checklist packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 2 toolchain packet",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`third_party/README.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

REQUIRED_DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

REQUIRED_BOOTSTRAP_NOTE_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
)

REQUIRED_TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`Documentation/zigux/review-checklist.md`",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
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
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_MANIFEST_VALUES = {
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
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
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def load_manifest(path: Path) -> dict:
    return json.loads(read_text(path))


def collect_marker_issues(code: str, text: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    review_text = read_text(root / REVIEW_CHECKLIST_REL)
    docs_readme_text = read_text(root / DOCS_README_REL)
    bootstrap_notes_text = read_text(root / BOOTSTRAP_NOTES_REL)
    scripts_readme_text = read_text(root / SCRIPTS_README_REL)
    tests_readme_text = read_text(root / TESTS_README_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    manifest = load_manifest(root / MANIFEST_REL)

    issues.extend(
        collect_marker_issues(
            "MISSING_REVIEW_CHECKLIST_MARKER", review_text, REQUIRED_REVIEW_CHECKLIST_MARKERS
        )
    )
    issues.extend(
        collect_marker_issues("MISSING_DOCS_ROOT_MARKER", docs_readme_text, REQUIRED_DOCS_ROOT_MARKERS)
    )
    issues.extend(
        collect_marker_issues(
            "MISSING_BOOTSTRAP_NOTE_MARKER", bootstrap_notes_text, REQUIRED_BOOTSTRAP_NOTE_MARKERS
        )
    )
    issues.extend(
        collect_marker_issues(
            "MISSING_SCRIPTS_README_MARKER", scripts_readme_text, REQUIRED_SCRIPTS_README_MARKERS
        )
    )
    issues.extend(
        collect_marker_issues("MISSING_TESTS_README_MARKER", tests_readme_text, REQUIRED_TESTS_README_MARKERS)
    )

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces"))
        return issues

    for key, expected_entries in REQUIRED_MANIFEST_VALUES.items():
        entries = present_surfaces.get(key)
        if not isinstance(entries, list):
            issues.append(("MISSING_MANIFEST_SECTION", f"present_surfaces.{key}"))
            continue
        for expected_entry in expected_entries:
            if expected_entry not in entries:
                issues.append(("MISSING_MANIFEST_ENTRY", f"{key}:{expected_entry}"))

    return issues


def run_checker(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE2_REVIEW_CHECKLIST_PACKET=fail")
        for code, detail in issues:
            print(f"PHASE2_REVIEW_CHECKLIST_PACKET_ISSUE={code}:{detail}")
        return 1

    print("PHASE2_REVIEW_CHECKLIST_PACKET=pass")
    return 0


def build_sample_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST_REL, "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / DOCS_README_REL, "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root / BOOTSTRAP_NOTES_REL, "\n".join(REQUIRED_BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(root / MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps({"present_surfaces": {key: list(values) for key, values in REQUIRED_MANIFEST_VALUES.items()}}, indent=2)
        + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        cases += 1

        path = root / REVIEW_CHECKLIST_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_REVIEW_CHECKLIST_MARKERS[0]))
        assert ("MISSING_REVIEW_CHECKLIST_MARKER", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / DOCS_README_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_DOCS_ROOT_MARKERS[0]))
        assert ("MISSING_DOCS_ROOT_MARKER", REQUIRED_DOCS_ROOT_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / BOOTSTRAP_NOTES_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_BOOTSTRAP_NOTE_MARKERS[0]))
        assert ("MISSING_BOOTSTRAP_NOTE_MARKER", REQUIRED_BOOTSTRAP_NOTE_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / SCRIPTS_README_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_SCRIPTS_README_MARKERS[0]))
        assert ("MISSING_SCRIPTS_README_MARKER", REQUIRED_SCRIPTS_README_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / TESTS_README_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_TESTS_README_MARKERS[0]))
        assert ("MISSING_TESTS_README_MARKER", REQUIRED_TESTS_README_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / MAKEFILE_REL
        text = read_text(path)
        write_text(path, replace_exact_line(text, REQUIRED_MAKEFILE_LINES[0]))
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        text = read_text(path)
        write_text(path, duplicate_exact_line(text, REQUIRED_MAKEFILE_LINES[0]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest_path = root / MANIFEST_REL
        manifest = load_manifest(manifest_path)
        del manifest["present_surfaces"]["review_surfaces"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_SECTION", "present_surfaces.review_surfaces") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest = load_manifest(manifest_path)
        manifest["present_surfaces"]["make_wrappers"] = ["zigux/Makefile"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_ENTRY", "make_wrappers:make -C zigux phase2-toolchain") in collect_issues(root)
        cases += 1

    print("PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to check")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    return run_checker(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
