#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    MAKEFILE_REL,
    WORKFLOW_REL,
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
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n",
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
    _require_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    _reject_snippets(makefile, FORBIDDEN_MAKEFILE_SNIPPETS, "unexpected_makefile_snippet", issues)
    _require_snippets(workflow, REQUIRED_WORKFLOW_SNIPPETS, "missing_workflow_snippet", issues)
    _reject_snippets(workflow, FORBIDDEN_WORKFLOW_SNIPPETS, "unexpected_workflow_snippet", issues)

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
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test\n"
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
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validation_flow_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root, MAKEFILE_REL, _fixture_makefile())
        _write(root, WORKFLOW_REL, _fixture_workflow())

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

    print("PHASE3_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE3_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=6")
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
        f"{len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
