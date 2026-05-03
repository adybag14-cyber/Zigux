#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"

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
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
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
    "name: Self-test Phase 3 wrapper generator",
    "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "name: Validate Phase 3 README tooling inventory",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "name: Self-test Phase 3 README tooling inventory checker",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
)

EXACT_ONCE_WORKFLOW_SNIPPETS = (
    "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
    "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
    "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
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

REQUIRED_DOCS_ROOT_SNIPPETS = (
    "`scripts/zigux/validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow are the validator-first route for the shared Phase 3 review packet; the dedicated survey scripts listed below stay supporting checks inside that shared gate rather than standalone release entrypoints.",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py` now keeps that dedicated low-level wrapper survey packet explicit alongside the broader roadmap-gap, export/UAPI, and policy/unsafe Phase 3 notes",
    "`scripts/zigux/validate-phase3-policy-unsafe-survey.py` remains a supporting survey check inside that shared validator-first route",
)

EXACT_ONCE_DOCS_ROOT_SNIPPETS = (
    "`scripts/zigux/validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow are the validator-first route for the shared Phase 3 review packet; the dedicated survey scripts listed below stay supporting checks inside that shared gate rather than standalone release entrypoints.",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py` remains a supporting survey check inside that shared validator-first route",
)

REQUIRED_SCRIPTS_README_SNIPPETS = (
    "`validate-phase3.py` is the validator-first entrypoint for the shared Phase 3 ABI and interop packet, and `make -C zigux phase3-validate` plus the bootstrap workflow replay that same route before the broader build-backed or survey-backed checks run.",
    "`validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that validator-first route rather than standalone bootstrap or release entrypoints.",
)

EXACT_ONCE_SCRIPTS_README_SNIPPETS = REQUIRED_SCRIPTS_README_SNIPPETS


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
    _require_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _require_exact_count(makefile, EXACT_ONCE_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet_count", 1, issues)
    _require_snippets(makefile, REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _reject_snippets(makefile, FORBIDDEN_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet", issues)
    _require_snippets(workflow, REQUIRED_WORKFLOW_SNIPPETS, "missing_workflow_snippet", issues)
    _require_exact_count(workflow, EXACT_ONCE_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet_count", 1, issues)
    _reject_snippets(workflow, FORBIDDEN_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet", issues)
    _require_snippets(docs_root, REQUIRED_DOCS_ROOT_SNIPPETS, "missing_docs_root_snippet", issues)
    _require_exact_count(docs_root, EXACT_ONCE_DOCS_ROOT_SNIPPETS, "unexpected_docs_root_snippet_count", 1, issues)
    _require_snippets(scripts_readme, REQUIRED_SCRIPTS_README_SNIPPETS, "missing_scripts_readme_snippet", issues)
    _require_exact_count(
        scripts_readme,
        EXACT_ONCE_SCRIPTS_README_SNIPPETS,
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
        "- `Documentation/zigux/phase3-rbtree-interop-survey.md` records the dedicated `rbtree` boundary packet, and `scripts/zigux/validate-phase3-rbtree-interop-survey.py` remains a supporting survey check inside that shared validator-first route.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[2]}, and `make -C zigux phase3-validate` now keeps that dedicated export-shim and UAPI boundary survey packet explicit alongside the broader roadmap-gap note.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[3]}, including the packet-local blob markers that make direct connector-era readback reviewable without a trustworthy branch-tip SHA.\n"
        f"- {REQUIRED_DOCS_ROOT_SNIPPETS[4]}, and `make -C zigux phase3-validate` plus the bootstrap workflow now keep that dedicated policy-and-unsafe survey packet explicit alongside the broader ABI slice note.\n"
    )


def _fixture_scripts_readme() -> str:
    return (
        "# scripts/zigux\n"
        "\n"
        "Phase 3 flow\n"
        f"- {REQUIRED_SCRIPTS_README_SNIPPETS[0]}\n"
        f"- {REQUIRED_SCRIPTS_README_SNIPPETS[1]}\n"
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validation_flow_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root, MAKEFILE_REL, _fixture_makefile())
        _write(root, WORKFLOW_REL, _fixture_workflow())
        _write(root, DOCS_ROOT_REL, _fixture_docs_root())
        _write(root, SCRIPTS_README_REL, _fixture_scripts_readme())

        baseline = validate(root)
        if baseline:
            raise SystemExit("phase3-validation-flow-self-test:baseline_failed:" + ",".join(baseline))

        makefile_path = root / MAKEFILE_REL
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-roadmap-gap-survey.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-roadmap-gap-survey.py\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        makefile_path.write_text(
            original_makefile
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-rbtree-interop-survey.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-rbtree-interop-survey.py\n"
            in issues
        )
        makefile_path.write_text(original_makefile, encoding="utf-8", newline="\n")

        workflow_path = root / WORKFLOW_REL
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "run: python3 scripts/zigux/check-phase3-validation-flow.py\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_workflow_snippet:run: python3 scripts/zigux/check-phase3-validation-flow.py\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow.replace(
                "run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_workflow_snippet:run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow.replace(
                "run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_workflow_snippet:run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Self-test Phase 3 wrapper generator again\n"
            + "        run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Validate Phase 3 wrapper templates again\n"
            + "        run: python3 scripts/zigux/generate-phase3-check-wrappers.py --check\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/generate-phase3-check-wrappers.py --check\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Validate Phase 3 README tooling inventory again\n"
            + "        run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Self-test Phase 3 README tooling inventory checker again\n"
            + "        run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet_count:2:run: python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Check Phase 3 roadmap gap survey\n"
            + "        run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet:run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        workflow_path.write_text(
            original_workflow
            + "      - name: Check Phase 3 rbtree interop survey\n"
            + "        run: python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_workflow_snippet:run: python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py\n"
            in issues
        )
        workflow_path.write_text(original_workflow, encoding="utf-8", newline="\n")

        docs_root_path = root / DOCS_ROOT_REL
        original_docs_root = docs_root_path.read_text(encoding="utf-8")
        docs_root_path.write_text(
            original_docs_root.replace(REQUIRED_DOCS_ROOT_SNIPPETS[0], "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_docs_root_snippet:" + REQUIRED_DOCS_ROOT_SNIPPETS[0]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        docs_root_path.write_text(
            original_docs_root + "\n- " + REQUIRED_DOCS_ROOT_SNIPPETS[0] + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_docs_root_snippet_count:2:" + REQUIRED_DOCS_ROOT_SNIPPETS[0]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        docs_root_path.write_text(
            original_docs_root.replace(REQUIRED_DOCS_ROOT_SNIPPETS[1], "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_docs_root_snippet:" + REQUIRED_DOCS_ROOT_SNIPPETS[1]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        docs_root_path.write_text(
            original_docs_root + "\n- " + REQUIRED_DOCS_ROOT_SNIPPETS[1] + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_docs_root_snippet_count:2:" + REQUIRED_DOCS_ROOT_SNIPPETS[1]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        docs_root_path.write_text(
            original_docs_root.replace(REQUIRED_DOCS_ROOT_SNIPPETS[2], "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_docs_root_snippet:" + REQUIRED_DOCS_ROOT_SNIPPETS[2]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        docs_root_path.write_text(
            original_docs_root + "\n- " + REQUIRED_DOCS_ROOT_SNIPPETS[2] + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_docs_root_snippet_count:2:" + REQUIRED_DOCS_ROOT_SNIPPETS[2]
            in issues
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8", newline="\n")

        scripts_readme_path = root / SCRIPTS_README_REL
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(REQUIRED_SCRIPTS_README_SNIPPETS[0], "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_scripts_readme_snippet:" + REQUIRED_SCRIPTS_README_SNIPPETS[0]
            in issues
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8", newline="\n")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(REQUIRED_SCRIPTS_README_SNIPPETS[1], "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "missing_scripts_readme_snippet:" + REQUIRED_SCRIPTS_README_SNIPPETS[1]
            in issues
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8", newline="\n")

        scripts_readme_path.write_text(
            original_scripts_readme + "\n- " + REQUIRED_SCRIPTS_README_SNIPPETS[0] + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_scripts_readme_snippet_count:2:" + REQUIRED_SCRIPTS_README_SNIPPETS[0]
            in issues
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8", newline="\n")

        scripts_readme_path.write_text(
            original_scripts_readme + "\n- " + REQUIRED_SCRIPTS_README_SNIPPETS[1] + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            "unexpected_scripts_readme_snippet_count:2:" + REQUIRED_SCRIPTS_README_SNIPPETS[1]
            in issues
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8", newline="\n")

    print("PHASE3_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE3_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=28")
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
        f"{len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_PHASE3_ABI_MAKEFILE_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS) + len(REQUIRED_DOCS_ROOT_SNIPPETS) + len(REQUIRED_SCRIPTS_README_SNIPPETS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
