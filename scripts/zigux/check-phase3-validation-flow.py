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
    "name: Check Phase 3 validation flow\n",
    "name: Self-test Phase 3 validator\n",
    "name: Self-test Phase 3 validation flow checker\n",
    "name: Self-test Phase 3 catalog\n",
    "name: Audit Phase 3 documentation sync\n",
    "name: Check Phase 3 slug sanity\n",
    "name: Self-test Phase 3 shared helper\n",
    "name: Self-test Phase 3 wrapper generator\n",
    "name: Validate Phase 3 wrapper templates\n",
    "name: Self-test Phase 3 runner\n",
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
DEFAULT_PHASE3_README_FLOW_SNIPPETS = (
    "`validate-phase3.py` is the validator-first entrypoint for the shared Phase 3 ABI and interop packet, and `make -C zigux phase3-validate` plus the bootstrap workflow replay that same route before the broader build-backed or survey-backed checks run.",
    "`validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that validator-first route rather than standalone bootstrap or release entrypoints.",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _require_snippets(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    issues: list[str],
) -> None:
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


def _reject_snippets(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    issues: list[str],
) -> None:
    for snippet in snippets:
        if snippet in text:
            issues.append(f"{prefix}:{snippet}")


def _find_duplicate_snippets(snippets: tuple[str, ...]) -> list[str]:
    duplicates: list[str] = []
    seen: set[str] = set()
    for snippet in snippets:
        if snippet in seen:
            if snippet not in duplicates:
                duplicates.append(snippet)
            continue
        seen.add(snippet)
    return duplicates


def _load_phase3_readme_flow_snippets(root: Path) -> tuple[tuple[str, ...], list[str]]:
    script_path = root / README_TOOLING_INVENTORY_REL
    if not script_path.exists():
        return (), [f"missing_file:{README_TOOLING_INVENTORY_REL}"]

    namespace = runpy.run_path(str(script_path))
    snippets = namespace.get("REQUIRED_PHASE3_FLOW_SNIPPETS")
    if not isinstance(snippets, tuple):
        return (), ["missing_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS"]
    if not all(isinstance(snippet, str) for snippet in snippets):
        return (), ["invalid_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS"]
    if len(snippets) != EXPECTED_PHASE3_README_FLOW_COUNT:
        return (), [
            "unexpected_phase3_flow_contract_count:"
            f"{len(snippets)}:{EXPECTED_PHASE3_README_FLOW_COUNT}"
        ]

    duplicates = _find_duplicate_snippets(snippets)
    if duplicates:
        return (), [
            f"duplicate_phase3_flow_contract_snippet:{snippet}"
            for snippet in duplicates
        ]

    return snippets, []


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
    readme_flow_snippets, contract_issues = _load_phase3_readme_flow_snippets(root)
    issues.extend(contract_issues)
    _require_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _require_exact_count(makefile, EXACT_ONCE_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet_count", 1, issues)
    _require_snippets(makefile, REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _reject_snippets(makefile, FORBIDDEN_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet", issues)
    _require_snippets(workflow, REQUIRED_WORKFLOW_SNIPPETS, "missing_workflow_snippet", issues)
    _require_exact_count(workflow, EXACT_ONCE_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet_count", 1, issues)
    _require_exact_count(workflow, EXACT_ONCE_WORKFLOW_TITLE_SNIPPETS, "unexpected_workflow_snippet_count", 1, issues)
    _reject_snippets(workflow, FORBIDDEN_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet", issues)
    _require_snippets(docs_root, REQUIRED_DOCS_ROOT_SNIPPETS, "missing_docs_root_snippet", issues)
    _require_exact_count(docs_root, EXACT_ONCE_DOCS_ROOT_SNIPPETS, "unexpected_docs_root_snippet_count", 1, issues)
    if readme_flow_snippets:
        _require_snippets(scripts_readme, readme_flow_snippets, "missing_scripts_readme_snippet", issues)
        _require_exact_count(
            scripts_readme,
            readme_flow_snippets,
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


def _fixture_scripts_readme() -> str:
    return (
        "# scripts/zigux\n"
        "\n"
        "Phase 3 flow\n"
        f"- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]}\n"
        f"- {DEFAULT_PHASE3_README_FLOW_SNIPPETS[1]}\n"
    )


def _fixture_readme_tooling_inventory(
    *snippets: str,
) -> str:
    if not snippets:
        snippets = DEFAULT_PHASE3_README_FLOW_SNIPPETS
    lines = ["REQUIRED_PHASE3_FLOW_SNIPPETS = ("]
    for snippet in snippets:
        lines.append(f'    "{snippet}",')
    lines.append(" )")
    lines.append("")
    return "\n".join(lines)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validation_flow_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root, MAKEFILE_REL, _fixture_makefile())
        _write(root, WORKFLOW_REL, _fixture_workflow())
        _write(root, DOCS_ROOT_REL, _fixture_docs_root())
        _write(root, SCRIPTS_README_REL, _fixture_scripts_readme())
        _write(root, README_TOOLING_INVENTORY_REL, _fixture_readme_tooling_inventory())

        baseline = validate(root)
        if baseline:
            raise SystemExit("phase3-validation-flow-self-test:baseline_failed:" + ",".join(baseline))

        duplicated_validation_flow_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n"
        )
        _write(root, MAKEFILE_REL, duplicated_validation_flow_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validation_flow_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_validate_phase3_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py\n"
        )
        _write(root, MAKEFILE_REL, duplicated_validate_phase3_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validate_phase3_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_validate_phase3_self_test_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n"
        )
        _write(root, MAKEFILE_REL, duplicated_validate_phase3_self_test_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validate_phase3_self_test_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_runner_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n"
        )
        _write(root, MAKEFILE_REL, duplicated_runner_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_runner_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_self_test_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test\n"
        )
        _write(root, MAKEFILE_REL, duplicated_catalog_self_test_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_self_test_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_audit_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, MAKEFILE_REL, duplicated_catalog_audit_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_audit_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_slug_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity\n"
        )
        _write(root, MAKEFILE_REL, duplicated_catalog_slug_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_slug_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_shared_helper_makefile = (
            _fixture_makefile()
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test\n"
        )
        _write(root, MAKEFILE_REL, duplicated_shared_helper_makefile)
        issues = validate(root)
        expected = [
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_shared_helper_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, MAKEFILE_REL, _fixture_makefile())
        duplicated_validation_flow_workflow = (
            _fixture_workflow()
            + "      - name: Check Phase 3 validation flow again\n"
            + "        run: python3 scripts/zigux/check-phase3-validation-flow.py\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validation_flow_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/check-phase3-validation-flow.py\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validation_flow_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_validate_phase3_workflow = (
            _fixture_workflow()
            + "      - name: Validate Phase 3 slices again\n"
            + "        run: python3 scripts/zigux/validate-phase3.py\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validate_phase3_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/validate-phase3.py\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validate_phase3_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_runner_workflow = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 runner again\n"
            + "        run: python3 scripts/zigux/run-phase3-checks.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_runner_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/run-phase3-checks.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_runner_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_validate_phase3_self_test_workflow = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 validator again\n"
            + "        run: python3 scripts/zigux/validate-phase3.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validate_phase3_self_test_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/validate-phase3.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validate_phase3_self_test_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_self_test_workflow = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 catalog again\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_catalog_self_test_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/phase3_catalog.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_self_test_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_audit_workflow = (
            _fixture_workflow()
            + "      - name: Audit Phase 3 documentation sync again\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, WORKFLOW_REL, duplicated_catalog_audit_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_audit_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_catalog_slug_workflow = (
            _fixture_workflow()
            + "      - name: Check Phase 3 slug sanity again\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --check-slug-sanity\n"
        )
        _write(root, WORKFLOW_REL, duplicated_catalog_slug_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/phase3_catalog.py --check-slug-sanity\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_catalog_slug_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_shared_helper_workflow = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 shared helper again\n"
            + "        run: python3 scripts/zigux/phase3_check_lib.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_shared_helper_workflow)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/phase3_check_lib.py --self-test\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_shared_helper_workflow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, MAKEFILE_REL, _fixture_makefile())
        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_validate_phase3_slices_workflow_title = (
            _fixture_workflow()
            + "      - name: Validate Phase 3 slices\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validate_phase3_slices_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Validate Phase 3 slices\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validate_phase3_slices_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_phase3_validator_workflow_title = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 validator\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_phase3_validator_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Self-test Phase 3 validator\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_phase3_validator_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_validation_flow_workflow_title = (
            _fixture_workflow()
            + "      - name: Check Phase 3 validation flow\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --check-slug-sanity\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validation_flow_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Check Phase 3 validation flow\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_validation_flow_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_validation_catalog_workflow_title = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 catalog\n"
            + "        run: python3 scripts/zigux/phase3_check_lib.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_validation_catalog_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Self-test Phase 3 catalog\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_phase3_catalog_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_audit_doc_sync_workflow_title = (
            _fixture_workflow()
            + "      - name: Audit Phase 3 documentation sync\n"
            + "        run: python3 scripts/zigux/phase3_check_lib.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_audit_doc_sync_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Audit Phase 3 documentation sync\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_audit_doc_sync_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_slug_sanity_workflow_title = (
            _fixture_workflow()
            + "      - name: Check Phase 3 slug sanity\n"
            + "        run: python3 scripts/zigux/phase3_check_lib.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_slug_sanity_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Check Phase 3 slug sanity\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_slug_sanity_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_shared_helper_workflow_title = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 shared helper\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_shared_helper_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Self-test Phase 3 shared helper\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_shared_helper_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_wrapper_generator_workflow_title = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 wrapper generator\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --self-test\n"
        )
        _write(root, WORKFLOW_REL, duplicated_wrapper_generator_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Self-test Phase 3 wrapper generator\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_wrapper_generator_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_wrapper_templates_workflow_title = (
            _fixture_workflow()
            + "      - name: Validate Phase 3 wrapper templates\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, WORKFLOW_REL, duplicated_wrapper_templates_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Validate Phase 3 wrapper templates\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_wrapper_templates_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_runner_workflow_title = (
            _fixture_workflow()
            + "      - name: Self-test Phase 3 runner\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, WORKFLOW_REL, duplicated_runner_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Self-test Phase 3 runner\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_runner_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        duplicated_readme_inventory_workflow_title = (
            _fixture_workflow()
            + "      - name: Validate Phase 3 README tooling inventory\n"
            + "        run: python3 scripts/zigux/phase3_catalog.py --audit-doc-sync\n"
        )
        _write(root, WORKFLOW_REL, duplicated_readme_inventory_workflow_title)
        issues = validate(root)
        expected = [
            "unexpected_workflow_snippet_count:2:name: Validate Phase 3 README tooling inventory\n",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_readme_inventory_workflow_title_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, WORKFLOW_REL, _fixture_workflow())
        _write(root, DOCS_ROOT_REL, _fixture_docs_root())
        duplicated_rbtree_docs_root = _fixture_docs_root() + f"- {REQUIRED_DOCS_ROOT_SNIPPETS[2]}\n"
        _write(root, DOCS_ROOT_REL, duplicated_rbtree_docs_root)
        issues = validate(root)
        expected = [
            f"unexpected_docs_root_snippet_count:2:{REQUIRED_DOCS_ROOT_SNIPPETS[2]}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_rbtree_docs_root_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_low_level_docs_root = _fixture_docs_root() + f"- {REQUIRED_DOCS_ROOT_SNIPPETS[4]}\n"
        _write(root, DOCS_ROOT_REL, duplicated_low_level_docs_root)
        issues = validate(root)
        expected = [
            f"unexpected_docs_root_snippet_count:2:{REQUIRED_DOCS_ROOT_SNIPPETS[4]}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_low_level_docs_root_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated_policy_docs_root = _fixture_docs_root() + f"- {REQUIRED_DOCS_ROOT_SNIPPETS[5]}\n"
        _write(root, DOCS_ROOT_REL, duplicated_policy_docs_root)
        issues = validate(root)
        expected = [
            f"unexpected_docs_root_snippet_count:2:{REQUIRED_DOCS_ROOT_SNIPPETS[5]}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_policy_docs_root_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, DOCS_ROOT_REL, _fixture_docs_root())
        duplicated_contract_snippet = DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]
        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            _fixture_readme_tooling_inventory(
                duplicated_contract_snippet,
                duplicated_contract_snippet,
            ),
        )
        issues = validate(root)
        expected = [
            f"duplicate_phase3_flow_contract_snippet:{duplicated_contract_snippet}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:duplicate_phase3_flow_contract_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        (root / README_TOOLING_INVENTORY_REL).unlink()
        issues = validate(root)
        expected = [f"missing_file:{README_TOOLING_INVENTORY_REL}"]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:missing_phase3_flow_contract_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root, README_TOOLING_INVENTORY_REL, "OTHER = ()\n")
        issues = validate(root)
        expected = ["missing_phase3_flow_contract:REQUIRED_PHASE3_FLOW_SNIPPETS"]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:missing_phase3_flow_contract_constant_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root,
            README_TOOLING_INVENTORY_REL,
            _fixture_readme_tooling_inventory(DEFAULT_PHASE3_README_FLOW_SNIPPETS[0]),
        )
        issues = validate(root)
        expected = [
            f"unexpected_phase3_flow_contract_count:1:{EXPECTED_PHASE3_README_FLOW_COUNT}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-validation-flow-self-test:unexpected_phase3_flow_contract_count_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        print("PHASE3_VALIDATION_FLOW_SELF_TEST=pass")
        print("PHASE3_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=60")
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
        f"{len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS) + len(REQUIRED_DOCS_ROOT_SNIPPETS) + EXPECTED_PHASE3_README_FLOW_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
