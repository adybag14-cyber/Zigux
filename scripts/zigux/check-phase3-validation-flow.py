#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_MAKEFILE_SNIPPETS = (
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)",
    "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate-phase3.py --self-test",
    "scripts/zigux/validate-phase3-roadmap-gap-survey.py --self-test",
    "scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
)

REQUIRED_WORKFLOW_SNIPPETS = (
    "name: Validate Phase 3 slices",
    "run: python3 scripts/zigux/validate-phase3.py",
    "name: Check Phase 3 roadmap gap survey",
    "run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py",
    "name: Check Phase 3 export and UAPI boundary survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "name: Check Phase 3 low-level wrapper boundary survey",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "name: Check Phase 3 policy and unsafe boundary survey",
    "run: python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "name: Self-test Phase 3 validator",
    "run: python3 scripts/zigux/validate-phase3.py --self-test",
    "name: Self-test Phase 3 roadmap gap survey checker",
    "run: python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py --self-test",
    "name: Self-test Phase 3 export and UAPI boundary survey checker",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "name: Self-test Phase 3 low-level wrapper boundary survey checker",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "name: Self-test Phase 3 policy and unsafe boundary survey checker",
    "run: python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "name: Run Phase 3 export/UAPI layout tests",
    "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    makefile = _read_text(root, MAKEFILE_REL, issues)
    workflow = _read_text(root, WORKFLOW_REL, issues)

    if makefile:
        _check_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    if workflow:
        _check_snippets(workflow, REQUIRED_WORKFLOW_SNIPPETS, "missing_workflow_snippet", issues)

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validation_flow_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
        _write(root, WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_SNIPPETS) + "\n")

        assert validate(root) == []

        reduced_workflow = tuple(
            snippet
            for snippet in REQUIRED_WORKFLOW_SNIPPETS
            if snippet
            not in (
                "name: Self-test Phase 3 low-level wrapper boundary survey checker",
                "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
                "name: Run Phase 3 export/UAPI layout tests",
                "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
            )
        )
        _write(root, WORKFLOW_REL, "\n".join(reduced_workflow) + "\n")
        issues = validate(root)
        assert (
            "missing_workflow_snippet:name: Self-test Phase 3 low-level wrapper boundary survey checker"
            in issues
        )
        assert (
            "missing_workflow_snippet:run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
            in issues
        )
        assert "missing_workflow_snippet:name: Run Phase 3 export/UAPI layout tests" in issues
        assert (
            "missing_workflow_snippet:run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"
            in issues
        )
        assert (
            "missing_workflow_snippet:name: Self-test Phase 3 policy and unsafe boundary survey checker"
            not in issues
        )

        _write(root, WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_SNIPPETS) + "\n")
        reduced_makefile = tuple(
            snippet
            for snippet in REQUIRED_MAKEFILE_SNIPPETS
            if snippet
            not in (
                "scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)",
                "scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
                "scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
                "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
            )
        )
        _write(root, MAKEFILE_REL, "\n".join(reduced_makefile) + "\n")
        issues = validate(root)
        assert (
            "missing_makefile_snippet:scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)"
            in issues
        )
        assert (
            "missing_makefile_snippet:scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
            in issues
        )
        assert (
            "missing_makefile_snippet:scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
            in issues
        )
        assert (
            "missing_makefile_snippet:zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"
            in issues
        )

    print("PHASE3_VALIDATION_FLOW_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 3 validation flow still carries the dedicated survey gates."
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
