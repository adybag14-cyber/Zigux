#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
THIRD_PARTY_README = Path("third_party/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REQUIRED_FILES = (
    SCRIPTS_README,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    TESTS_README,
    THIRD_PARTY_README,
    WORKFLOW,
    MAKEFILE,
    POLICY,
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/README.md`",
    "`third_party/README.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
)

THIRD_PARTY_README_MARKERS = (
    "# Zigux third-party archives",
    "## Current pinned Zig archive contract",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

WORKFLOW_MARKERS = (
    "name: zigux-bootstrap",
    "env:",
    "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "- name: Setup pinned Zig toolchain",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
)

MAKEFILE_MARKERS = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "phase2: phase2-validate",
)

EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

STALE_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def require_absent(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{prefix}:stale:{marker}")


def load_required_make_routes(root: Path) -> list[str]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit("invalid policy shape: upgrade_policy")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list):
        raise SystemExit("invalid policy shape: required_make_routes")
    return [route for route in routes if isinstance(route, str)]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    scripts_readme = read_text(resolve(root, SCRIPTS_README))
    bootstrap_notes = read_text(resolve(root, BOOTSTRAP_NOTES))
    review_checklist = read_text(resolve(root, REVIEW_CHECKLIST))
    tests_readme = read_text(resolve(root, TESTS_README))
    third_party_readme = read_text(resolve(root, THIRD_PARTY_README))
    workflow = read_text(resolve(root, WORKFLOW))
    makefile = read_text(resolve(root, MAKEFILE))

    require_markers(scripts_readme, SCRIPTS_README_MARKERS, "scripts_readme", failures)
    require_markers(bootstrap_notes, BOOTSTRAP_NOTES_MARKERS, "bootstrap_notes", failures)
    require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", failures)
    require_markers(tests_readme, TESTS_README_MARKERS, "tests_readme", failures)
    require_markers(third_party_readme, THIRD_PARTY_README_MARKERS, "third_party_readme", failures)
    require_markers(workflow, WORKFLOW_MARKERS, "workflow", failures)
    require_markers(makefile, MAKEFILE_MARKERS, "makefile", failures)
    require_absent(scripts_readme, STALE_MARKERS, "scripts_readme", failures)

    routes = load_required_make_routes(root)
    if tuple(routes) != EXPECTED_REQUIRED_MAKE_ROUTES:
        failures.append(
            "policy:required_make_routes:"
            + ",".join(routes)
        )

    return failures


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, SCRIPTS_README),
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "## Phase 2",
                "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, the current manifest-backed bridge and fixdep helpers, and the rematerialized make-wrapper routes instead of reopening older missing-route stories.",
                "- `scripts/zigux/check-genksyms-bridge.py` stays part of the returned scripts-root packet.",
                "- `third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path.",
                "- `scripts/zigux/check-phase2-docs-shared-reminder.py` and `scripts/zigux/check-phase2-required-make-routes.py` remain part of the same scripts-root packet.",
                "- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards.",
                "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`.",
                "- keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet.",
                "- `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` remain the returned Phase 2 make-wrapper routes.",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "\n".join(
            [
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "## Current direct packet",
                "- `scripts/zigux/check-phase2-docs-shared-reminder.py`",
                "- `scripts/zigux/check-phase2-tests-readme-alignment.py`",
                "- `scripts/zigux/check-phase2-required-make-routes.py`",
                "- `scripts/zigux/check-phase2-tool-manifest.py`",
                "- `scripts/zigux/check-phase2-artifact-tools-manifest.py`",
                "- `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
                "- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
                "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, REVIEW_CHECKLIST),
        "\n".join(
            [
                "# Zigux Review Checklist",
                "",
                "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `scripts/zigux/README.md`, `third_party/README.md`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` still agree on the current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet while the current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet stay explicit too?",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, TESTS_README),
        "\n".join(
            [
                "# zigux/tests",
                "",
                "## Phase 2 review packet",
                "- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
                "- `scripts/zigux/README.md`",
                "- `scripts/zigux/check-phase2-docs-shared-reminder.py`",
                "- `scripts/zigux/check-phase2-tests-readme-alignment.py`",
                "- `scripts/zigux/check-phase2-tool-manifest.py`",
                "- `scripts/zigux/check-phase2-artifact-tools-manifest.py`",
                "- `scripts/zigux/check-phase2-required-make-routes.py`",
                "- `scripts/zigux/install-zig.py`",
                "- `scripts/zigux/check-phase2-cross.py`",
                "- Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
                "- keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, THIRD_PARTY_README),
        "\n".join(
            [
                "# Zigux third-party archives",
                "",
                "## Current pinned Zig archive contract",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "- size: `58159088` bytes",
                "- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, WORKFLOW),
        "\n".join(
            [
                "name: zigux-bootstrap",
                "",
                "env:",
                "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
                "",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "      - run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
                "      - run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
                "      - run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                "      - run: python3 scripts/zigux/check-phase2-cross.py",
                "      - run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                "      - run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, MAKEFILE),
        "\n".join(
            [
                ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                "",
                "phase2-toolchain:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
                "",
                "phase2-tools:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
                "",
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
                "",
                "phase2-genksyms:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
                "",
                "phase2-fixdep:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
                "",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
                "",
                "phase2: phase2-validate",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    build_sample_root(root)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane18_phase2_scripts_readme_") as tmp:
        sample_root = Path(tmp) / "sample"
        write_sample_root(sample_root)
        failures = validate(sample_root)
        if failures:
            raise SystemExit(
                "PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST=fail\n"
                + "\n".join(failures)
            )

        broken_root = Path(tmp) / "broken"
        write_sample_root(broken_root)
        broken_scripts = resolve(broken_root, SCRIPTS_README)
        broken_scripts.write_text(
            broken_scripts.read_text(encoding="utf-8").replace(
                "`make -C zigux phase2-fixdep`", "`make -C zigux phase2-fixdep-missing`", 1
            ),
            encoding="utf-8",
        )
        broken_failures = validate(broken_root)
        if not any(failure.startswith("scripts_readme:missing:") for failure in broken_failures):
            raise SystemExit("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST=fail\nmissing negative coverage")

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT=2")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Guard the Phase 2 scripts-root toolchain packet against reminder drift."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test cases")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return

    if args.self_test:
        run_self_test()
        return

    failures = validate(args.root)
    if failures:
        raise SystemExit(
            "PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=fail\n" + "\n".join(failures)
        )

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_MAKE_ROUTES)}")


if __name__ == "__main__":
    main()
