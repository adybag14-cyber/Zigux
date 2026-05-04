#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else Path.cwd().resolve()
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
README_TOOLING_INVENTORY_REL = "scripts/zigux/check-phase3-readme-tooling-inventory.py"

REQUIRED_FILES = (
    MAKEFILE_REL,
    WORKFLOW_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
)

REQUIRED_MAKEFILE_SNIPPETS = (
    "phase3-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n",
)

EXACT_ONCE_MAKEFILE_SNIPPETS = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n",
)

REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS = (
    "phase3-abi:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig\n",
)

FORBIDDEN_MAKEFILE_SNIPPETS = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-roadmap-gap-survey.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-rbtree-interop-survey.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-roadmap-gap-survey.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-rbtree-interop-survey.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test\n",
)

REQUIRED_WORKFLOW_SNIPPETS = (
    "name: Validate Phase 3 slices",
    "run: python3 scripts/zigux/validate-phase3.py\n",
    "name: Self-test Phase 3 ABI duplicate declaration checker",
    "run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n",
    "name: Check Phase 3 ABI duplicate declarations",
    "run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py\n",
    "name: Check Phase 3 validation flow",
    "run: python3 scripts/zigux/check-phase3-validation-flow.py\n",
    "name: Self-test Phase 3 validator",
    "run: python3 scripts/zigux/validate-phase3.py --self-test\n",
    "name: Self-test Phase 3 validation flow checker",
    "run: python3 scripts/zigux/check-phase3-validation-flow.py --self-test\n",
    "name: Validate Phase 3 wrapper templates\n",
    "run: python3 scripts/zigux/run-phase3-checks.py --self-test\n",
    "name: Validate Phase 3 README tooling inventory",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "name: Self-test Phase 3 README tooling inventory checker",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
)

EXACT_ONCE_WORKFLOW_SNIPPETS = (
    "run: python3 scripts/zigux/validate-phase3.py\n",
    "run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n",
    "run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py\n",
    "run: python3 scripts/zigux/check-phase3-validation-flow.py\n",
    "run: python3 scripts/zigux/validate-phase3.py --self-test\n",
    "run: python3 scripts/zigux/check-phase3-validation-flow.py --self-test\n",
    "run: python3 scripts/zigux/phase3_catalog.py --self-test\n",
    "run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n",
    "run: python3 scripts/zigux/phase3_catalog.py --check-slug-sanity\n",
    "run: python3 scripts/zigux/phase3_check_lib.py --self-test\n",
    "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
    "run: python3 scripts/zigux/run-phase3-checks.py --self-test\n",
)

EXACT_ONCE_WORKFLOW_TITLE_SNIPPETS = (
    "name: Validate Phase 3 slices\n",
    "name: Self-test Phase 3 ABI duplicate declaration checker\n",
    "name: Check Phase 3 ABI duplicate declarations\n",
    "name: Check Phase 3 validation flow\n",
    "name: Self-test Phase 3 validator\n",
    "name: Self-test Phase 3 validation flow checker\n",
    "name: Self-test Phase 3 catalog\n",
    "name: Audit Phase 3 documentation sync\n",
    "name: Check Phase 3 slug sanity\n",
    "name: Self-test Phase 3 shared helper\n",
    "name: Self-test Phase 3 runner\n",
    "name: Self-test Phase 3 wrapper generator\n",
    "name: Validate Phase 3 wrapper templates\n",
    "name: Validate Phase 3 README tooling inventory\n",
    "name: Self-test Phase 3 README tooling inventory checker\n",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py\n",
    "run: python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py\n",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py\n",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py\n",
    "run: python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py\n",
    "run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py --self-test\n",
    "run: python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py --self-test\n",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test\n",
    "run: python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test\n",
)

REQUIRED_DOCS_ROOT_RBTREE_SNIPPET = (
    "`Documentation/zigux/phase3-rbtree-interop-survey.md` records the dedicated `rbtree` boundary packet, "
    "and `scripts/zigux/validate-phase3-rbtree-interop-survey.py` remains a supporting survey check inside "
    "that shared validator-first route."
)

REQUIRED_DOCS_ROOT_SNIPPETS = (
    "`scripts/zigux/validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow are the "
    "validator-first route for the shared Phase 3 review packet; the dedicated survey scripts listed below stay "
    "supporting checks inside that shared gate rather than standalone release entrypoints.",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py` remains a supporting survey check inside that shared validator-first route",
    REQUIRED_DOCS_ROOT_RBTREE_SNIPPET,
    "`scripts/zigux/validate-phase3-export-uapi-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py` now keeps that dedicated low-level wrapper survey packet explicit alongside the broader roadmap-gap, export/UAPI, and policy/unsafe Phase 3 notes",
    "`scripts/zigux/validate-phase3-policy-unsafe-survey.py` remains a supporting survey check inside that shared validator-first route",
)

EXACT_ONCE_DOCS_ROOT_SNIPPETS = REQUIRED_DOCS_ROOT_SNIPPETS

EXPECTED_PHASE3_README_FLOW_COUNT = 2
EXPECTED_CROSS_PHASE_README_FLOW_COUNT = 3

DEFAULT_PHASE3_README_FLOW_SNIPPETS = (
    "`validate-phase3.py` is the validator-first entrypoint for the shared Phase 3 ABI and interop packet, and `make -C zigux phase3-validate` plus the bootstrap workflow replay that same route before the broader build-backed or survey-backed checks run.",
    "`validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that validator-first route rather than standalone bootstrap or release entrypoints.",
)

DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS = (
    "`validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.",
    "`validate-phase8.py` is the validator-first entrypoint for the parked repo-hosted tooling packet across `tools/lib/subcmd/exec-cmd.zig`, `tools/lib/subcmd/help.zig`, `tools/lib/symbol/kallsyms.zig`, the helper-first `tools/lib/bpf/zigux_segments/` rollout, and the bounded `perf_buffer__poll(timeout_ms)` bookkeeping adjunct.",
    "`validate-phase9.py` is the validator-first entrypoint for the shared runtime-pilot packet across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/README.md`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _require_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def _require_exact_count(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    expected_count: int,
    issues: list[str],
) -> None:
    for snippet in snippets:
        actual_count = text.count(snippet)
        if actual_count != expected_count:
            issues.append(f"{prefix}:{actual_count}:{snippet}")


def _reject_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet in text:
            issues.append(f"{prefix}:{snippet}")


def _find_duplicate_snippets(snippets: tuple[str, ...]) -> list[str]:
    duplicates: list[str] = []
    seen: set[str] = set()
    for snippet in snippets:
        if snippet in seen and snippet not in duplicates:
            duplicates.append(snippet)
        seen.add(snippet)
    return duplicates


def _load_readme_flow_snippets(
    root: Path,
    constant_name: str,
    expected_count: int,
    missing_issue: str,
    invalid_issue: str,
    count_issue_prefix: str,
    duplicate_issue_prefix: str,
) -> tuple[tuple[str, ...], list[str]]:
    script_path = root / README_TOOLING_INVENTORY_REL
    if not script_path.exists():
        return (), [f"missing_file:{README_TOOLING_INVENTORY_REL}"]

    namespace = runpy.run_path(str(script_path))
    snippets = namespace.get(constant_name)
    if not isinstance(snippets, tuple):
        return (), [missing_issue]
    if not all(isinstance(snippet, str) for snippet in snippets):
        return (), [invalid_issue]
    if len(snippets) != expected_count:
        return (), [f"{count_issue_prefix}:{len(snippets)}:{expected_count}"]

    duplicates = _find_duplicate_snippets(snippets)
    if duplicates:
        return (), [f"{duplicate_issue_prefix}:{snippet}" for snippet in duplicates]

    return snippets, []


def _load_phase3_readme_flow_snippets(root: Path) -> tuple[tuple[str, ...], list[str]]:
    return _load_readme_flow_snippets(
        root,
        "REQUIRED_PHASE3_FLOW_SNIPPETS",
        EXPECTED_PHASE3_README_FLOW_COUNT,
        "missing_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS",
        "invalid_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS",
        "unexpected_phase3_flow_contract_count",
        "duplicate_phase3_flow_contract_snippet",
    )


def _load_cross_phase_readme_flow_snippets(root: Path) -> tuple[tuple[str, ...], list[str]]:
    return _load_readme_flow_snippets(
        root,
        "REQUIRED_CROSS_PHASE_FLOW_SNIPPETS",
        EXPECTED_CROSS_PHASE_README_FLOW_COUNT,
        "missing_cross_phase_flow_contract:REQUIRED_CROSS_PHASE_FLOW_SNIPPETS",
        "invalid_cross_phase_flow_contract:REQUIRED_CROSS_PHASE_FLOW_SNIPPETS",
        "unexpected_cross_phase_flow_contract_count",
        "duplicate_cross_phase_flow_contract_snippet",
    )


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    makefile = _read_text(root, MAKEFILE_REL, issues)
    workflow = _read_text(root, WORKFLOW_REL, issues)
    docs_root = _read_text(root, DOCS_ROOT_REL, issues)
    scripts_readme = _read_text(root, SCRIPTS_README_REL, issues)
    phase3_flow_snippets, phase3_contract_issues = _load_phase3_readme_flow_snippets(root)
    cross_phase_flow_snippets, cross_phase_contract_issues = _load_cross_phase_readme_flow_snippets(root)
    issues.extend(phase3_contract_issues)
    issues.extend(cross_phase_contract_issues)

    _require_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _require_exact_count(
        makefile,
        EXACT_ONCE_MAKEFILE_SNIPPETS,
        "unexpected_makefile_snippet_count",
        1,
        issues,
    )
    _require_snippets(makefile, REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _reject_snippets(makefile, FORBIDDEN_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet", issues)

    _require_snippets(workflow, REQUIRED_WORKFLOW_SNIPPETS, "missing_workflow_snippet", issues)
    _require_exact_count(
        workflow,
        EXACT_ONCE_WORKFLOW_SNIPPETS,
        "unexpected_workflow_snippet_count",
        1,
        issues,
    )
    _require_exact_count(
        workflow,
        EXACT_ONCE_WORKFLOW_TITLE_SNIPPETS,
        "unexpected_workflow_snippet_count",
        1,
        issues,
    )
    _reject_snippets(workflow, FORBIDDEN_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet", issues)

    _require_snippets(docs_root, REQUIRED_DOCS_ROOT_SNIPPETS, "missing_docs_root_snippet", issues)
    _require_exact_count(
        docs_root,
        EXACT_ONCE_DOCS_ROOT_SNIPPETS,
        "unexpected_docs_root_snippet_count",
        1,
        issues,
    )

    if phase3_flow_snippets:
        _require_snippets(scripts_readme, phase3_flow_snippets, "missing_scripts_readme_snippet", issues)
        _require_exact_count(
            scripts_readme,
            phase3_flow_snippets,
            "unexpected_scripts_readme_snippet_count",
            1,
            issues,
        )
    if cross_phase_flow_snippets:
        _require_snippets(
            scripts_readme,
            cross_phase_flow_snippets,
            "missing_scripts_readme_snippet",
            issues,
        )
        _require_exact_count(
            scripts_readme,
            cross_phase_flow_snippets,
            "unexpected_scripts_readme_snippet_count",
            1,
            issues,
        )

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _fixture_makefile() -> str:
    return (
        "phase3-validate:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-duplicate-declarations.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n"
        "\n"
        "phase3-abi:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\n"
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig\n"
    )


def _fixture_workflow() -> str:
    return (
        "jobs:\n"
        "  bootstrap:\n"
        "    steps:\n"
        "      - name: Validate Phase 3 slices\n"
        "        run: python3 scripts/zigux/validate-phase3.py\n"
        "      - name: Self-test Phase 3 ABI duplicate declaration checker\n"
        "        run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py --self-test\n"
        "      - name: Check Phase 3 ABI duplicate declarations\n"
        "        run: python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py\n"
        "      - name: Check Phase 3 validation flow\n"
        "        run: python3 scripts/zigux/check-phase3-validation-flow.py\n"
        "      - name: Self-test Phase 3 validator\n"
        "        run: python3 scripts/zigux/validate-phase3.py --self-test\n"
        "      - name: Self-test Phase 3 validation flow checker\n"
        "        run: python3 scripts/zigux/check-phase3-validation-flow.py --self-test\n"
        "      - name: Self-test Phase 3 catalog\n"
        "        run: python3 scripts/zigux/phase3_catalog.py --self-test\n"
        "      - name: Audit Phase 3 documentation sync\n"
        "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        "      - name: Check Phase 3 slug sanity\n"
        "        run: python3 scripts/zigux/phase3_catalog.py --check-slug-sanity\n"
        "      - name: Self-test Phase 3 shared helper\n"
        "        run: python3 scripts/zigux/phase3_check_lib.py --self-test\n"
        "      - name: Self-test Phase 3 runner\n"
        "        run: python3 scripts/zigux/run-phase3-checks.py --self-test\n"
        "      - name: Self-test Phase 3 wrapper generator\n"
        "        run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
        "      - name: Validate Phase 3 wrapper templates\n"
        "        run: python3 scripts/zigux/generate-phase3-check-wrappers.py --check\n"
        "      - name: Self-test Phase 3 README tooling inventory checker\n"
        "        run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n"
        "      - name: Validate Phase 3 README tooling inventory\n"
        "        run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
    )


def _fixture_docs_root() -> str:
    return (
        "# Zigux Documentation\n"
        "\n"
        "Phase 3 notes\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[0]}\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[1]}, and `make -C zigux phase3-validate` plus the bootstrap workflow keep that survey note explicit.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[2]}\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[3]}, and `make -C zigux phase3-validate` now keeps that dedicated export-shim and UAPI boundary survey packet explicit alongside the broader roadmap-gap note.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[4]}, including the packet-local blob markers that make direct connector-era readback reviewable without a trustworthy branch-tip SHA.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[5]}, and `make -C zigux phase3-validate` plus the bootstrap workflow now keep that dedicated policy-and-unsafe survey packet explicit alongside the broader ABI slice note.\n"
    )


def _fixture_scripts_readme(
    phase3_snippets: tuple[str, ...] = DEFAULT_PHASE3_README_FLOW_SNIPPETS,
    cross_phase_snippets: tuple[str, ...] = DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS,
) -> str:
    return (
        "# scripts/zigux\n"
        "\n"
        "Phase 3 flow\n"
        f"- {phase3_snippets[0]}\n"
        f"- {phase3_snippets[1]}\n"
        "Phase 6 flow\n"
        f"- {cross_phase_snippets[0]}\n"
        "Phase 8 flow\n"
        f"- {cross_phase_snippets[1]}\n"
        "Phase 9 flow\n"
        f"- {cross_phase_snippets[2]}\n"
    )


def _fixture_readme_tooling_inventory(
    phase3_snippets: tuple[str, ...] = DEFAULT_PHASE3_README_FLOW_SNIPPETS,
    cross_phase_snippets: tuple[str, ...] = DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS,
) -> str:
    lines = ["REQUIRED_PHASE3_FLOW_SNIPPETS = ("]
    for snippet in phase3_snippets:
        lines.append(f'    "{snippet}",')
    lines.append(")")
    lines.append("")
    lines.append("REQUIRED_CROSS_PHASE_FLOW_SNIPPETS = (")
    for snippet in cross_phase_snippets:
        lines.append(f'    "{snippet}",')
    lines.append(")")
    lines.append("")
    return "\n".join(lines)


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        raise SystemExit(
            f"phase3-validation-flow-self-test:{label}:"
            + (",".join(issues) if issues else "none")
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validation_flow_") as tmp_dir:
        root = Path(tmp_dir)

        def reset_tree() -> None:
            _write(root, MAKEFILE_REL, _fixture_makefile())
            _write(root, WORKFLOW_REL, _fixture_workflow())
            _write(root, DOCS_ROOT_REL, _fixture_docs_root())
            _write(root, SCRIPTS_README_REL, _fixture_scripts_readme())
            _write(root, README_TOOLING_INVENTORY_REL, _fixture_readme_tooling_inventory())

        reset_tree()
        baseline = validate(root)
        if baseline:
            raise SystemExit("phase3-validation-flow-self-test:baseline_failed:" + ",".join(baseline))

        case_count = 0

        for snippet in EXACT_ONCE_MAKEFILE_SNIPPETS:
            reset_tree()
            _write(root, MAKEFILE_REL, _fixture_makefile() + snippet)
            _assert_only(
                validate(root),
                [f"unexpected_makefile_snippet_count:2:{snippet}"],
                f"duplicate_makefile_snippet_guard_failed_{case_count}",
            )
            case_count += 1

        for snippet in EXACT_ONCE_WORKFLOW_SNIPPETS:
            reset_tree()
            _write(root, WORKFLOW_REL, _fixture_workflow() + "      - duplicate\n        " + snippet)
            _assert_only(
                validate(root),
                [f"unexpected_workflow_snippet_count:2:{snippet}"],
                f"duplicate_workflow_snippet_guard_failed_{case_count}",
            )
            case_count += 1

        for snippet in EXACT_ONCE_WORKFLOW_TITLE_SNIPPETS:
            reset_tree()
            _write(
                root,
                WORKFLOW_REL,
                _fixture_workflow()
                + f"      - {snippet}        run: python3 scripts/zigux/phase3-title-probe.py\n",
            )
            _assert_only(
                validate(root),
                [f"unexpected_workflow_snippet_count:2:{snippet}"],
                f"duplicate_workflow_title_guard_failed_{case_count}",
            )
            case_count += 1

        for snippet in (
            REQUIRED_DOCS_ROOT_SNIPPETS[0],
            REQUIRED_DOCS_ROOT_SNIPPETS[1],
            REQUIRED_DOCS_ROOT_SNIPPETS[2],
            REQUIRED_DOCS_ROOT_SNIPPETS[3],
            REQUIRED_DOCS_ROOT_SNIPPETS[4],
            REQUIRED_DOCS_ROOT_SNIPPETS[5],
        ):
            reset_tree()
            _write(root, DOCS_ROOT_REL, _fixture_docs_root() + f"- {snippet}\n")
            _assert_only(
                validate(root),
                [f"unexpected_docs_root_snippet_count:2:{snippet}"],
                f"duplicate_docs_root_guard_failed_{case_count}",
            )
            case_count += 1

        reset_tree()
        duplicated_phase3 = DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            _fixture_readme_tooling_inventory(
                (duplicated_phase3, duplicated_phase3),
                DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS,
            ),
        )
        _assert_only(
            validate(root),
            [f"duplicate_phase3_flow_contract_snippet:{duplicated_phase3}"],
            f"duplicate_phase3_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(root, README_TOOLING_INVENTORY_REL, "OTHER = ()\n")
        _assert_only(
            validate(root),
            [
                "missing_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS",
                "missing_cross_phase_flow_contract:REQUIRED_CROSS_PHASE_FLOW_SNIPPETS",
            ],
            f"missing_phase3_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(root, README_TOOLING_INVENTORY_REL, _fixture_readme_tooling_inventory((DEFAULT_PHASE3_README_FLOW_SNIPPETS[0],), DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS))
        _assert_only(
            validate(root),
            [f"unexpected_phase3_flow_contract_count:1:{EXPECTED_PHASE3_README_FLOW_COUNT}"],
            f"phase3_contract_count_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            "REQUIRED_PHASE3_FLOW_SNIPPETS = (1, 2)\nREQUIRED_CROSS_PHASE_FLOW_SNIPPETS = ()\n",
        )
        _assert_only(
            validate(root),
            [
                "invalid_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS",
                f"unexpected_cross_phase_flow_contract_count:0:{EXPECTED_CROSS_PHASE_README_FLOW_COUNT}",
            ],
            f"invalid_phase3_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        duplicated_cross_phase = DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[1]
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            _fixture_readme_tooling_inventory(
                DEFAULT_PHASE3_README_FLOW_SNIPPETS,
                (
                    DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0],
                    duplicated_cross_phase,
                    duplicated_cross_phase,
                ),
            ),
        )
        _assert_only(
            validate(root),
            [f"duplicate_cross_phase_flow_contract_snippet:{duplicated_cross_phase}"],
            f"duplicate_cross_phase_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(root, README_TOOLING_INVENTORY_REL, "REQUIRED_PHASE3_FLOW_SNIPPETS = ()\nOTHER = ()\n")
        _assert_only(
            validate(root),
            [
                f"unexpected_phase3_flow_contract_count:0:{EXPECTED_PHASE3_README_FLOW_COUNT}",
                "missing_cross_phase_flow_contract:REQUIRED_CROSS_PHASE_FLOW_SNIPPETS",
            ],
            f"missing_cross_phase_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            _fixture_readme_tooling_inventory(
                DEFAULT_PHASE3_README_FLOW_SNIPPETS,
                (DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0],),
            ),
        )
        _assert_only(
            validate(root),
            [f"unexpected_cross_phase_flow_contract_count:1:{EXPECTED_CROSS_PHASE_README_FLOW_COUNT}"],
            f"cross_phase_contract_count_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            "\n".join(
                [
                    "REQUIRED_PHASE3_FLOW_SNIPPETS = (",
                    *[f'    "{snippet}",' for snippet in DEFAULT_PHASE3_README_FLOW_SNIPPETS],
                    ")",
                    "",
                    "REQUIRED_CROSS_PHASE_FLOW_SNIPPETS = (1, 2, 3)",
                    "",
                ]
            ),
        )
        _assert_only(
            validate(root),
            ["invalid_cross_phase_flow_contract:REQUIRED_CROSS_PHASE_FLOW_SNIPPETS"],
            f"invalid_cross_phase_contract_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        (root / README_TOOLING_INVENTORY_REL).unlink()
        _assert_only(
            validate(root),
            [
                f"missing_file:{README_TOOLING_INVENTORY_REL}",
                f"missing_file:{README_TOOLING_INVENTORY_REL}",
            ],
            f"missing_inventory_file_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        (root / MAKEFILE_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{MAKEFILE_REL}"],
            f"missing_makefile_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        (root / WORKFLOW_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{WORKFLOW_REL}"],
            f"missing_workflow_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            SCRIPTS_README_REL,
            "# scripts/zigux\n"
            "\n"
            "Phase 3 flow\n"
            f"- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[1]}\n"
            "Phase 6 flow\n"
            f"- {DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0]}\n"
            "Phase 8 flow\n"
            f"- {DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[1]}\n"
            "Phase 9 flow\n"
            f"- {DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[2]}\n",
        )
        _assert_only(
            validate(root),
            [
                f"missing_scripts_readme_snippet:{DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}",
                f"unexpected_scripts_readme_snippet_count:0:{DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}",
            ],
            f"missing_phase3_readme_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            SCRIPTS_README_REL,
            _fixture_scripts_readme() + f"\n- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}\n",
        )
        _assert_only(
            validate(root),
            [f"unexpected_scripts_readme_snippet_count:2:{DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}"],
            f"duplicate_phase3_readme_guard_failed_{case_count}",
        )
        case_count += 1

        reset_tree()
        _write(
            root,
            SCRIPTS_README_REL,
            "# scripts/zigux\n"
            "\n"
            "Phase 3 flow\n"
            f"- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}\n"
            f"- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[1]}\n"
            "Phase 8 flow\n"
            f"- {DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[1]}\n"
            "Phase 9 flow\n"
            f"- {DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[2]}\n",
        )
        _assert_only(
            validate(root),
            [
                f"missing_scripts_readme_snippet:{DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0]}",
                f"unexpected_scripts_readme_snippet_count:0:{DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0]}",
            ],
            f"missing_cross_phase_readme_guard_failed_{case_count}",
        )
        case_count += 1

        for snippet, label in (
            (DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[0], "duplicate_phase6_readme_guard_failed"),
            (DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[1], "duplicate_phase8_readme_guard_failed"),
            (DEFAULT_CROSS_PHASE_README_FLOW_SNIPPETS[2], "duplicate_phase9_readme_guard_failed"),
        ):
            reset_tree()
            _write(root, SCRIPTS_README_REL, _fixture_scripts_readme() + f"\n- {snippet}\n")
            _assert_only(
                validate(root),
                [f"unexpected_scripts_readme_snippet_count:2:{snippet}"],
                f"{label}_{case_count}",
            )
            case_count += 1

        reset_tree()
        _write(root, DOCS_ROOT_REL, "# Zigux Documentation\n")
        _assert_only(
            validate(root),
            [
                f"missing_docs_root_snippet:{snippet}" for snippet in REQUIRED_DOCS_ROOT_SNIPPETS
            ] + [
                f"unexpected_docs_root_snippet_count:0:{snippet}" for snippet in REQUIRED_DOCS_ROOT_SNIPPETS
            ],
            f"missing_docs_root_packet_guard_failed_{case_count}",
        )
        case_count += 1

        if case_count != 69:
            raise SystemExit(f"phase3-validation-flow-self-test:unexpected_case_count:{case_count}")

        print("PHASE3_VALIDATION_FLOW_SELF_TEST=pass")
        print("PHASE3_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=69")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 3 validation route stays validator-first."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_VALIDATION_FLOW=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_VALIDATION_FLOW=pass")
    print(
        "PHASE3_VALIDATION_FLOW_MARKER_COUNT="
        f"{len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS) + len(REQUIRED_DOCS_ROOT_SNIPPETS) + EXPECTED_PHASE3_README_FLOW_COUNT + EXPECTED_CROSS_PHASE_README_FLOW_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
